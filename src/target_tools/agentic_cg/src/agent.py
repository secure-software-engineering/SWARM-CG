import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import litellm

from prompts import get_prompt
from tools import TOOL_DISPATCH, TOOL_SCHEMAS, submit_answers as _submit_answers_fn

logger = logging.getLogger("agent")

# Suppress verbose litellm logging
litellm.suppress_debug_info = True
logging.getLogger("litellm").setLevel(logging.WARNING)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# ── Hermes/Qwen-style <tool_call> parser ─────────────────────────────────────
# Some models (Qwen3, Mistral via vLLM, etc.) emit tool calls as XML tags in
# the content field rather than the structured tool_calls API field.

_TOOL_CALL_RE = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


@dataclass
class _SyntheticFunction:
    name: str
    arguments: str  # JSON-encoded string, same as real tool_call.function.arguments


@dataclass
class _SyntheticToolCall:
    id: str
    function: _SyntheticFunction


_THINK_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL)


def _extract_thinking(msg) -> str:
    """Extract reasoning/thinking tokens from an LLM response message.
    Handles: Qwen3/DeepSeek <think> tags in content, OpenAI o1 reasoning_content,
    and Anthropic extended thinking content blocks."""
    # 1. Dedicated reasoning_content field (OpenAI o1, Deepseek R1 via litellm)
    if getattr(msg, "reasoning_content", None):
        return msg.reasoning_content
    # 2. Dedicated thinking field (some providers)
    if getattr(msg, "thinking", None):
        return msg.thinking
    # 3. Anthropic extended thinking: content is a list of typed blocks
    if isinstance(msg.content, list):
        parts = [b.get("thinking", "") for b in msg.content
                 if isinstance(b, dict) and b.get("type") == "thinking"]
        if parts:
            return "\n".join(parts)
    # 4. Qwen3 / DeepSeek R1 native: <think>...</think> in content string
    if isinstance(msg.content, str):
        blocks = _THINK_RE.findall(msg.content)
        if blocks:
            return "\n".join(blocks)
    return ""


def _text_content(msg) -> str:
    """Return only the visible (non-thinking) text from an assistant message.
    Strips <think> blocks from string content; extracts text-typed blocks from list content."""
    if isinstance(msg.content, list):
        parts = [b.get("text", "") for b in msg.content
                 if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(parts).strip()
    if isinstance(msg.content, str):
        return _THINK_RE.sub("", msg.content).strip()
    return ""


def _parse_tool_calls_from_content(content: str) -> list[_SyntheticToolCall]:
    """
    Extract <tool_call>{"name": ..., "arguments": {...}}</tool_call> blocks
    from assistant content and return them as synthetic tool-call objects that
    are duck-type compatible with the real litellm tool_call objects.
    """
    calls = []
    for i, match in enumerate(_TOOL_CALL_RE.finditer(content)):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse <tool_call> block {i}: {e}")
            continue
        name = data.get("name", "")
        # "arguments" key is standard; some templates use "parameters"
        args = data.get("arguments", data.get("parameters", {}))
        calls.append(
            _SyntheticToolCall(
                id=f"synthetic_{i}",
                function=_SyntheticFunction(
                    name=name,
                    arguments=json.dumps(args),
                ),
            )
        )
    return calls


class AgenticCallGraphBuilder:
    def __init__(
        self,
        model: str,
        api_key: Optional[str],
        api_base: Optional[str],
        max_iterations: int,
        temperature: float,
        prompt_id: str = "detailed",
    ):
        self.model = model
        self.api_key = api_key or None
        self.api_base = api_base or None
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.prompt_id = prompt_id
        self.system_prompt = get_prompt(prompt_id)

    def build_call_graph(self, file_path: str, benchmark_dir: str, gt_summary: dict | None = None) -> tuple[dict, list]:
        """
        Run the agentic tool-calling loop for a single benchmark directory.
        Returns (call_graph, trajectory) where:
          - call_graph: final call graph dict in SWARM-CG format ({} on failure)
          - trajectory: list of step dicts recording the full agent interaction
        """
        # If gt_summary is provided, save the mapping file so submit_answers can use it
        if gt_summary is not None:
            mapping_file = Path(benchmark_dir) / ".swarmcg_mapping.json"
            question_to_func = {}
            for i, entry in enumerate(gt_summary["functions"], start=1):
                question_to_func[i] = entry["qualified_name"]
            mapping_data = {
                "question_to_func": question_to_func,
                "module": gt_summary.get("module", Path(file_path).stem)
            }
            with open(mapping_file, "w") as f:
                json.dump(mapping_data, f)
        
        messages = self._build_initial_messages(file_path, benchmark_dir, gt_summary)
        trajectory = [
            {
                "step": 0,
                "role": "user",
                "content": messages[-1]["content"],
            }
        ]

        for iteration in range(self.max_iterations):
            logger.debug(f"Iteration {iteration + 1}/{self.max_iterations} for {file_path}")

            try:
                response = self._call_llm(messages)
            except Exception as e:
                logger.error(f"LLM call failed on iteration {iteration + 1}: {e}")
                trajectory.append({
                    "step": iteration + 1,
                    "role": "error",
                    "content": str(e),
                })
                raise

            assistant_msg = response.choices[0].message

            thinking = _extract_thinking(assistant_msg)
            visible_content = _text_content(assistant_msg)

            # Build assistant dict for message history — use cleaned content so
            # <think> blocks don't accumulate and bloat the context window.
            assistant_dict = {"role": "assistant", "content": visible_content}
            if assistant_msg.tool_calls:
                assistant_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_msg.tool_calls
                ]
            messages.append(assistant_dict)

            # Capture raw response metadata for trajectory
            usage = response.usage
            raw = {
                "id": getattr(response, "id", None),
                "model": getattr(response, "model", None),
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                } if usage else None,
            }

            # Record assistant step in trajectory
            traj_step = {
                "step": iteration + 1,
                "role": "assistant",
                "thinking": thinking,
                "thought": visible_content,
                "tool_calls": [],
                "raw": raw,
            }

            # Resolve tool calls: prefer the structured field; fall back to
            # parsing <tool_call>...</tool_call> blocks from the content for
            # Hermes/Qwen-style models served via vLLM.
            tool_calls = assistant_msg.tool_calls
            if not tool_calls:
                tool_calls = _parse_tool_calls_from_content(assistant_msg.content or "")
                if tool_calls:
                    logger.info(
                        f"Parsed {len(tool_calls)} tool call(s) from content "
                        f"(Hermes/Qwen format) on iteration {iteration + 1}."
                    )

            if not tool_calls:
                logger.warning(
                    f"LLM returned plain text on iteration {iteration + 1}, nudging."
                )
                nudge = (
                    "You must call submit_answers (or submit_call_graph) to provide your answer. "
                    "Do not respond with plain text."
                )
                traj_step["tool_calls"] = []
                trajectory.append(traj_step)
                trajectory.append({"step": iteration + 1, "role": "nudge", "content": nudge})
                messages.append({"role": "user", "content": nudge})
                continue

            # Process all tool calls in this turn
            tool_result_messages = []
            submit_result = None

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    tool_result = f"ERROR: Could not parse tool arguments: {e}"
                    tool_args = None

                if tool_args is not None:
                    if tool_name in ("submit_call_graph", "submit_answers"):
                        try:
                            if tool_name == "submit_answers":
                                # Pass benchmark_dir (local variable, not shared instance state)
                                # so submit_answers finds the correct mapping file.
                                # Using self._current_benchmark_dir would race when the same
                                # agent instance serves multiple threads (max_workers > 1).
                                answers_val = tool_args.get("answers", tool_args) if isinstance(tool_args, dict) else tool_args
                                submit_result_msg = _submit_answers_fn(answers_val, _benchmark_dir=benchmark_dir)
                            else:
                                submit_result_msg = TOOL_DISPATCH[tool_name](tool_args)
                            parsed = json.loads(submit_result_msg)
                            if "call_graph" in parsed:
                                # submit_answers returns the parsed call graph in its result
                                submit_result = parsed["call_graph"]
                            else:
                                # submit_call_graph: extract from args (accept flat or wrapped)
                                submit_result = tool_args.get("call_graph", tool_args)
                        except (ValueError, KeyError) as e:
                            tool_result = f"ERROR: Invalid submission: {e}. Please fix and resubmit."
                            traj_step["tool_calls"].append({
                                "name": tool_name,
                                "arguments": tool_args,
                                "response": tool_result,
                            })
                            tool_result_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": tool_result,
                            })
                            submit_result = None
                            continue

                        traj_step["tool_calls"].append({
                            "name": tool_name,
                            "arguments": tool_args,
                            "response": submit_result_msg,
                        })
                        tool_result_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": submit_result_msg,
                        })
                        trajectory.append(traj_step)
                        messages.extend(tool_result_messages)
                        return submit_result, trajectory
                    else:
                        tool_result = self._execute_tool_call(tool_name, tool_args)
                else:
                    tool_result = "ERROR: Could not parse tool arguments"

                traj_step["tool_calls"].append({
                    "name": tool_name,
                    "arguments": tool_args if tool_args is not None else {},
                    "response": tool_result,
                })
                tool_result_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result,
                })

            trajectory.append(traj_step)
            messages.extend(tool_result_messages)

        logger.warning(f"Max iterations ({self.max_iterations}) reached for {file_path}")
        trajectory.append({
            "step": self.max_iterations + 1,
            "role": "system",
            "content": f"Terminated: max_iterations ({self.max_iterations}) reached without submission.",
        })
        return {}, trajectory

    def _build_initial_messages(
        self, file_path: str, benchmark_dir: str, gt_summary: dict | None = None
    ) -> list:
        if gt_summary is not None:
            questions_text = "\n".join(gt_summary["questions"])
            func_list = "\n".join(
                f"  - {e['qualified_name']}" for e in gt_summary["functions"]
            )
            user_content = (
                f"Please construct the call graph for the Python benchmark at: `{file_path}`\n"
                f"The benchmark directory containing this test case is: `{benchmark_dir}`\n\n"
                f"The following questions have been pre-generated for you. "
                f"You do NOT need to call `get_call_sites` or `list_directory`.\n\n"
                f"**Questions:**\n{questions_text}\n\n"
                f"**Functions to include as keys in submit_answers:**\n{func_list}\n\n"
                "Steps:\n"
                "1. Call read_file on main.py (and any imported local modules) to understand "
                "the code and resolve call targets to fully qualified names.\n"
                "2. Call submit_answers with your answers: a dict mapping each function's "
                "qualified name to a comma-separated string of its callees "
                "(empty string if it makes no calls)."
            )
        else:
            user_content = (
                f"Please construct the call graph for the Python benchmark at: `{file_path}`\n"
                f"The benchmark directory containing this test case is: `{benchmark_dir}`\n\n"
                "Steps:\n"
                "1. Call list_directory on the benchmark directory.\n"
                "2. Call get_call_sites on main.py — this returns all function definitions and "
                "a list of questions to answer about each function's call sites.\n"
                "3. Call read_file on main.py (and any imported local modules) to understand "
                "the code and resolve call targets to fully qualified names.\n"
                "4. Call submit_answers with your answers: a dict mapping each function's "
                "qualified name to a comma-separated string of its callees "
                "(empty string if it makes no calls)."
            )
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]

    def _call_llm(self, messages: list):
        kwargs = dict(
            model=self.model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=self.temperature,
        )
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.api_base:
            kwargs["api_base"] = self.api_base

        return litellm.completion(**kwargs)

    def _execute_tool_call(self, tool_name: str, tool_args: dict) -> str:
        if tool_name not in TOOL_DISPATCH:
            return f"ERROR: Unknown tool '{tool_name}'"
        try:
            result = TOOL_DISPATCH[tool_name](tool_args)
            return result if isinstance(result, str) else json.dumps(result)
        except PermissionError as e:
            return f"ERROR: {e}"
        except FileNotFoundError as e:
            return f"ERROR: {e}"
        except NotADirectoryError as e:
            return f"ERROR: {e}"
        except Exception as e:
            logger.warning(f"Tool '{tool_name}' raised unexpected error: {e}")
            return f"ERROR: {e}"
