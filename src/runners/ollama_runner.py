import os
from core.base_runner import BaseRunner

class OllamaRunner(BaseRunner):
    def __init__(self, host_results_path, config):
        super().__init__("ollama", "./target_tools/ollama", host_results_path)
        self.config = config

    def run_tool_test(self):
        super().run_tool_test()
        # Add specific logic for running Ollama
        self.logger.info("Running Ollama-specific logic")
