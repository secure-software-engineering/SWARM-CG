import os
import time

import docker
from .base_runner import BaseRunner
from core import setup_logger

# Create a logger
logger = setup_logger("LLM Runner", "llm_runner.log")


class LLMRunner(BaseRunner):

    def __init__(
        self,
        host_results_path,
        config,
        debug=False,
        nocache=False,
        language=None,
        benchmark_name=None,
    ):
        super().__init__(
            "llms",
            "./target_tools/llms",
            host_results_path,
            nocache=nocache,
            volumes={
                os.path.abspath("/mnt/hf_cache/huggingface"): {
                    "bind": "/root/.cache/huggingface",
                    "mode": "rw",
                }
            },
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
                self.config["llm"]["openai_key"],
                "--hf_token",
                self.config["llm"]["hf_token"],
                "--prompt_id",
                self.config["llm"]["prompt_id"],
            ]
            for i in ["models", "custom_models", "openai_models"]:
                if self.config["llm"][i]:
                    command_to_run.append(f"--{i}")
                    command_to_run.extend(self.config["llm"][i])

            _, response = self.container.exec_run(" ".join(command_to_run), stream=True)
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running LLM test in container: {e}")
            raise

    def copy_results_from_container(self):
        for i in ["models", "custom_models", "openai_models"]:
            if self.config["llm"][i]:
                for model in self.config["llm"][i]:
                    model_results_path = f"/tmp/{model}/benchmarks"
                    self.file_handler.copy_files_from_container(
                        self.container,
                        model_results_path,
                        f"{self.host_results_path}/{model}",
                    )

    def spawn_docker_instance(self):
        logger.info("Creating container")
        container = self.docker_client.containers.run(
            self.tool_name,
            detach=True,
            stdin_open=True,
            tty=True,
            volumes=self.volumes,
            runtime="nvidia",
            device_requests=[
                docker.types.DeviceRequest(
                    count=-1, capabilities=[["gpu"]]
                )  # Request all available GPUs
            ],
        )
        return container
