import sys
from src.cli.main import main
from core import setup_logger, load_config
from runners import OllamaRunner

# Set up logging
logger = setup_logger("main_runner", "logs/main_runner.log")
CONFIG_FILE = "config.yaml"

def initialize_runners(host_results_path, config, selected_runners):
    """
    Initialize runner instances based on the selected runner names.
    """
    available_runners = {
        "ollama": OllamaRunner,
    }

    initialized_runners = []
    for runner_name in selected_runners:
        if runner_name in available_runners:
            RunnerClass = available_runners[runner_name]
            # Pass config to OllamaRunner, or other runners needing specific configurations
            if runner_name == "ollama":
                runner_instance = RunnerClass(host_results_path, config)
            else:
                runner_instance = RunnerClass(host_results_path)
            initialized_runners.append(runner_instance)
        else:
            logger.error(f"Unknown runner: {runner_name}")
            sys.exit(-1)

    return initialized_runners

def main():
     # Parse arguments and load configuration
    args = main.get_args()
    config = load_config(CONFIG_FILE)

if __name__ == "__main__":
    main()