import os
import logging
from core import setup_logger

class BaseRunner:
    def __init__(self, tool_name, dockerfile_path, host_results_path):
        self.tool_name = tool_name
        self.dockerfile_path = dockerfile_path
        self.host_results_path = host_results_path
        self.logger = setup_logger(self.tool_name, f"logs/{self.tool_name}.log")

        if not os.path.exists(self.host_results_path):
            os.makedirs(self.host_results_path)

    def run_tool_test(self):
        self.logger.info(f"Running tool test for {self.tool_name}")
        # tool-specific test logic
