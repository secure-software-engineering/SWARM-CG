import argparse
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import litellm
from tqdm import tqdm

from agent import AgenticCallGraphBuilder
from tools import _generate_questions_from_gt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("runner")

# Suppress litellm's own verbose output
litellm.suppress_debug_info = True
logging.getLogger("litellm").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def trajectory_to_markdown(trajectory: list, file_path: str) -> str:
    """Convert a trajectory list to a human-readable markdown string."""
    lines = []
    lines.append(f"# Agent Trajectory\n")
    lines.append(f"**File:** `{file_path}`\n")
    lines.append(f"**Steps:** {len([s for s in trajectory if s['role'] == 'assistant'])}\n")
    lines.append("---\n")

    for step in trajectory:
        role = step["role"]

        if role == "user":
            lines.append("## Task\n")
            lines.append(f"{step['content']}\n")
            lines.append("---\n")

        elif role == "assistant":
            lines.append(f"## Step {step['step']}\n")

            # Token usage
            raw = step.get("raw", {})
            usage = (raw.get("usage") or {}) if raw else {}
            pts = usage.get("prompt_tokens")
            cts = usage.get("completion_tokens")
            if pts is not None or cts is not None:
                lines.append(f"*Tokens: {pts} prompt / {cts} completion*\n")

            # Thinking tokens (collapsible)
            if step.get("thinking"):
                lines.append("<details><summary>💭 Thinking</summary>\n")
                lines.append(f"\n{step['thinking']}\n\n</details>\n")

            if step.get("thought"):
                lines.append("### Thought\n")
                lines.append(f"{step['thought']}\n")

            for tc in step.get("tool_calls", []):
                name = tc["name"]
                args = tc["arguments"]
                response = tc["response"]

                lines.append(f"### Tool: `{name}`\n")

                if name in ("read_file", "list_directory", "get_call_sites"):
                    lines.append("**Arguments:**\n")
                    lines.append(f"```\n{args.get('path', '')}\n```\n")
                    lines.append("**Response:**\n")
                    lang = "python" if name == "read_file" else "json" if name == "get_call_sites" else ""
                    lines.append(f"```{lang}\n{response}\n```\n")

                elif name == "submit_call_graph":
                    lines.append("**Call graph submitted:**\n")
                    try:
                        cg = args.get("call_graph", {})
                        pretty = json.dumps(cg, indent=2)
                    except (TypeError, ValueError):
                        pretty = str(args)
                    lines.append(f"```json\n{pretty}\n```\n")
                    try:
                        resp = json.loads(response)
                        status = resp.get("status", "?")
                        count = resp.get("count", "?")
                        lines.append(f"**Result:** {status} — {count} function(s)\n")
                    except (json.JSONDecodeError, TypeError):
                        lines.append(f"**Result:** {response}\n")

                else:
                    lines.append(f"**Arguments:**\n```json\n{json.dumps(args, indent=2)}\n```\n")
                    lines.append(f"**Response:**\n```\n{response}\n```\n")

            lines.append("---\n")

        elif role == "nudge":
            lines.append(f"### Warning: Nudge\n")
            lines.append(f"> {step['content']}\n")

        elif role == "error":
            lines.append(f"### Error (step {step['step']})\n")
            lines.append(f"```\n{step['content']}\n```\n")
            lines.append("---\n")

        elif role == "system":
            lines.append(f"## Terminated\n")
            lines.append(f"{step['content']}\n")

    return "\n".join(lines)


def list_benchmark_files(folder_path: str) -> list:
    """Return all main.py files recursively — one agent run per test case directory."""
    return sorted(Path(folder_path).rglob("main.py"))


def process_one(agent: AgenticCallGraphBuilder, file_path: Path, questions_mode: str = "ast") -> bool:
    """Process a single benchmark test case. Returns True on success, False on error."""
    result_path = file_path.parent / "main_result.json"
    trajectory_path = file_path.parent / "main_trajectory.json"
    md_path = file_path.parent / "main_trajectory.md"
    try:
        gt_summary = None
        if questions_mode == "ground_truth":
            gt_path = file_path.parent / "callgraph.json"
            if gt_path.exists():
                with open(gt_path) as f:
                    gt_data = json.load(f)
                gt_summary = _generate_questions_from_gt(gt_data, file_path.stem, file_path.name)
                logger.info(f"GT questions loaded for {file_path}: {len(gt_data)} functions")
            else:
                logger.warning(f"callgraph.json not found at {gt_path}, falling back to AST mode")

        logger.info(f"Processing: {file_path}")
        call_graph, trajectory = agent.build_call_graph(
            file_path=str(file_path),
            benchmark_dir=str(file_path.parent),
            gt_summary=gt_summary,
        )
        with open(result_path, "w") as f:
            json.dump(call_graph, f, indent=4, sort_keys=True)
        with open(trajectory_path, "w") as f:
            json.dump(trajectory, f, indent=4, ensure_ascii=False)
        with open(md_path, "w") as f:
            f.write(trajectory_to_markdown(trajectory, str(file_path)))
        logger.info(f"Saved call graph with {len(call_graph)} entries to {result_path}")
        return True
    except Exception as e:
        logger.error(f"Failed on {file_path}: {e}")
        with open(result_path, "w") as f:
            json.dump({}, f)
        return False


def main_runner(args):
    agent = AgenticCallGraphBuilder(
        model=args.model,
        api_key=args.api_key if args.api_key else None,
        api_base=args.api_base if args.api_base and args.api_base != "null" else None,
        max_iterations=args.max_iterations,
        temperature=args.temperature,
    )

    benchmark_files = list_benchmark_files(args.benchmark_path)
    logger.info(
        f"Found {len(benchmark_files)} test files in {args.benchmark_path} "
        f"(max_workers={args.max_workers})"
    )
    error_count = 0

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(process_one, agent, fp, args.questions_mode): fp for fp in benchmark_files}
        with tqdm(total=len(futures), desc="Benchmarks", unit="test") as pbar:
            for future in as_completed(futures):
                if not future.result():
                    error_count += 1
                pbar.update(1)

    logger.info(f"Runner finished. Processed {len(benchmark_files)} files. Errors: {error_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentic LLM call graph construction runner")
    parser.add_argument(
        "--benchmark_path",
        default="/tmp/benchmarks",
        help="Path to the benchmark directory",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="LiteLLM model string (e.g. gpt-4o, ollama/llama3, anthropic/claude-sonnet-4-5)",
    )
    parser.add_argument(
        "--api_key",
        default="",
        help="API key for the LLM provider (empty for Ollama or env-var-based auth)",
    )
    parser.add_argument(
        "--api_base",
        default="null",
        help="Custom API base URL (e.g. http://localhost:11434 for Ollama)",
    )
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=10,
        help="Maximum tool-calling iterations per file before giving up",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="LLM sampling temperature",
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=1,
        help="Number of test cases to process in parallel (default: 1 = sequential)",
    )
    parser.add_argument(
        "--questions_mode",
        default="ast",
        choices=["ast", "ground_truth"],
        help=(
            "Source for generating per-function questions. "
            "'ast' (default): questions derived from AST analysis of main.py. "
            "'ground_truth': questions derived from callgraph.json (requires callgraph.json "
            "to be present in the container — useful for evaluation, not production)."
        ),
    )

    args = parser.parse_args()

    # Allow env vars to fill in unset args (convenient for local dev)
    # Priority: CLI arg > env var > default
    if not args.api_key:
        args.api_key = os.environ.get("OPENAI_API_KEY", "")
    if args.api_base == "null":
        env_base = os.environ.get("OPENAI_BASE_URL", "") or os.environ.get("OPENAI_API_BASE", "")
        if env_base:
            args.api_base = env_base

    main_runner(args)
