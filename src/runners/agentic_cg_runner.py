from .base_runner import BaseRunner
from core import setup_logger, strip_python_comments

logger = setup_logger("AgenticCG Runner", "agentic_cg_runner.log")


class AgenticCGRunner(BaseRunner):

    def __init__(
        self,
        host_results_path,
        config,
        debug=False,
        nocache=False,
        language=None,
        benchmark_name=None,
        models=None,
    ):
        super().__init__(
            "agentic_cg", "./target_tools/agentic_cg", host_results_path, nocache=nocache
        )
        self.config = config
        self.language = language
        self.benchmark_name = benchmark_name
        self.model = config.get("agentic_cg", {}).get("model", "gpt-4o-mini")
        self.questions_mode = config.get("agentic_cg", {}).get("questions_mode", "ast")
        # In ground_truth mode, callgraph.json must reach the container so runner.py can
        # generate questions from it. In normal (ast) mode, exclude it so the LLM can't cheat.
        if self.questions_mode == "ground_truth":
            self.copy_exclude_extensions = [".md"]
        else:
            self.copy_exclude_extensions = [".json", ".md"]
        self.copy_py_content_filter = strip_python_comments     # strip comments so LLM can't read hints

    @property
    def results_dir_name(self):
        # Model names from OpenAI-compatible endpoints often contain slashes
        # (e.g. "openai/Qwen/Qwen3-30B"). Replace with underscores so the
        # result lands in a single flat directory that the analyzer can find.
        sanitized_model = self.model.replace("/", "_")
        return f"{self.tool_name}_{sanitized_model}"

    def run_test_in_session(self):
        try:
            cfg = self.config.get("agentic_cg", {})
            command_to_run = [
                "python",
                self.test_runner_script_path,
                "--benchmark_path",
                self.benchmark_path,
                "--model",
                str(cfg.get("model", "gpt-4o-mini")),
                "--api_key",
                str(cfg.get("api_key", "")),
                "--api_base",
                str(cfg.get("api_base", "null")),
                "--max_iterations",
                str(cfg.get("max_iterations", 10)),
                "--temperature",
                str(cfg.get("temperature", 0.1)),
                "--max_workers",
                str(cfg.get("max_workers", 1)),
                "--questions_mode",
                str(cfg.get("questions_mode", "ast")),
                "--prompt_id",
                str(cfg.get("prompt_id", "detailed")),
            ]
            _, response = self.container.exec_run(" ".join(command_to_run), stream=True)
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running AgenticCG test in container: {e}")
            raise

    def copy_results_from_container(self):
        try:
            model_results_path = "/tmp/benchmarks"
            logger.info(f"Copying results from: {model_results_path}")
            self.file_handler.copy_files_from_container(
                self.container,
                model_results_path,
                f"{self.host_results_path}/{self.results_dir_name}",
            )
        except Exception as e:
            logger.error(f"Error copying results for AgenticCG: {e}")
            raise
