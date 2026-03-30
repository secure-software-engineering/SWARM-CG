import os
import time

from .base_runner import BaseRunner
from core import setup_logger

# Create a logger
logger = setup_logger("LiteLLM Runner", "litellm_runner.log")


class LiteLLMRunner(BaseRunner):

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
            "litellm",
            "./target_tools/litellm",
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
                "--language",
                self.language,
                "--prompt_id",
                self.config["litellm"]["prompt_id"],
            ]
            
            # Add API base if provided
            if "api_base" in self.config["litellm"] and self.config["litellm"]["api_base"]:
                command_to_run.append("--api_base")
                command_to_run.append(self.config["litellm"]["api_base"])
            
            # Add models
            if "models" in self.config["litellm"] and self.config["litellm"]["models"]:
                command_to_run.append("--models")
                command_to_run.extend(self.config["litellm"]["models"])
            
            # Add max_workers if provided
            if "max_workers" in self.config["litellm"]:
                command_to_run.append("--max_workers")
                command_to_run.append(str(self.config["litellm"]["max_workers"]))

            # Set up environment variables for API authentication
            # LiteLLM uses standard environment variables like OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.
            env_vars = {}
            if "api_key" in self.config["litellm"] and self.config["litellm"]["api_key"]:
                # For custom endpoints/proxies, set OPENAI_API_KEY as the default
                env_vars["OPENAI_API_KEY"] = self.config["litellm"]["api_key"]
                # Also set a generic LITELLM_API_KEY for proxy authentication
                env_vars["LITELLM_API_KEY"] = self.config["litellm"]["api_key"]

            _, response = self.container.exec_run(
                " ".join(command_to_run), 
                stream=True,
                environment=env_vars if env_vars else None
            )
            for line in response:
                logger.info(line)
        except Exception as e:
            logger.error(f"Error running LiteLLM test in container: {e}")
            raise

    def copy_results_from_container(self):
        if "models" in self.config["litellm"] and self.config["litellm"]["models"]:
            for model in self.config["litellm"]["models"]:
                model_safe_name = model.replace("/", "_").replace(":", "_")
                model_results_path = f"/tmp/{model_safe_name}/benchmarks"
                self.file_handler.copy_files_from_container(
                    self.container,
                    model_results_path,
                    f"{self.host_results_path}/{model_safe_name}",
                )
