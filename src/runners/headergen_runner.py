import os
import time

import docker
from .base_runner import BaseRunner
from core import setup_logger

# Create a logger
logger = setup_logger("HeaderGen CS Runner", "hg_runner.log")


class HeaderGenCSRunner(BaseRunner):
    def __init__(
        self,
        host_results_path,
        config,
        debug=False,
        nocache=False,
        language=None,
        benchmark_name=None,
    ):
        if debug:
            super().__init__(
                "headergen_cs",
                "./target_tools/headergen_cs",
                host_results_path,
                dockerfile_name="Dockerfile.dev",
                nocache=nocache,
                volumes={
                    "/mnt/Projects/PhD/Research/HeaderGen/git_sources/HeaderGen_github/": {
                        "bind": "/app/HeaderGen",
                        "mode": "ro",
                    },
                },
            )
        else:
            super().__init__(
                "headergen_cs",
                "./target_tools/headergen_cs",
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
                "--benchmark_path",
                self.benchmark_path,
            ]
            _, response = self.container.exec_run(" ".join(command_to_run), stream=True)
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running HeaderGen test in container: {e}")
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
            logger.error(f"Error copying results for Ollama models: {e}")
            raise
