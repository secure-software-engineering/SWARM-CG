import time
from .base_runner import BaseRunner
from core import setup_logger

# Create a logger
logger = setup_logger("jelly Runner", "jelly_runner.log")


class JellyRunner(BaseRunner):

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
        if debug:
            super().__init__(
                "jelly",
                "./target_tools/jelly",
                host_results_path,
                nocache=nocache,
                volumes={
                    "/mnt/d/UPB/Thesis/SWARM-CG/SWARM-CG/src/target_tools/jelly/src": {
                        "bind": "/tmp/src",
                        "mode": "ro",
                    },
                },
            )
        else:
            super().__init__(
                "jelly",
                "./target_tools/jelly",
                host_results_path,
                nocache=nocache,
            )
        self.config = config
        self.language = language
        self.benchmark_name = benchmark_name

    def run_test_in_session(self):
        try:
            command_to_run = [
                "python",
                self.test_runner_script_path,
                "--language",
                self.language,
            ]
            _, response = self.container.exec_run(" ".join(command_to_run), stream=True)
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running jelly test in container: {e}")
            raise

    def copy_results_from_container(self):
        try:
            model_results_path = f"/tmp/benchmarks"
            logger.info(f"searching for this path: {model_results_path}")
            self.file_handler.copy_files_from_container(
                self.container,
                model_results_path,
                f"{self.host_results_path}/{self.tool_name}",
            )
        except Exception as e:
            logger.error(f"Error copying results for jelly models: {e}")
            raise
