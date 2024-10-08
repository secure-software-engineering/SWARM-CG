import time
from .base_runner import BaseRunner
from core import setup_logger

# Create a logger
logger = setup_logger("Ollama Runner", "ollama_runner.log")


class OllamaRunner(BaseRunner):

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
            "ollama", "./target_tools/ollama", host_results_path, nocache=nocache
        )
        self.config = config
        self.language = language
        self.benchmark_name = benchmark_name

    def run_test_in_session(self):
        try:
            command_to_run = [
                "python",
                self.test_runner_script_path,
                "--benchmark_path",
                self.benchmark_path,
                "--language",
                self.language,
                "--openai_key",
                self.config["ollama"]["openai_key"],
                "--ollama_url",
                self.config["ollama"]["ollama_url"],
                "--prompt_id",
                self.config["ollama"]["prompt_id"],
                "--ollama_models",
            ]
            command_to_run.extend(self.config["ollama"]["ollama_models"])

            _, response = self.container.exec_run(" ".join(command_to_run), stream=True)
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running Ollama test in container: {e}")
            raise

    def copy_results_from_container(self):
        try:
            for model in self.config["ollama"]["ollama_models"]:
                model_results_path = f"/tmp/{model}/benchmarks"
                logger.info(f"searching for this path: {model_results_path}")
                self.file_handler.copy_files_from_container(
                    self.container,
                    model_results_path,
                    f"{self.host_results_path}/{model}",
                )
        except Exception as e:
            logger.error(f"Error copying results for Ollama models: {e}")
            raise
