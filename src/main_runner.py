import os
import shutil
import sys
from runners import OllamaRunner
from cli import parse_runner_args
from core import load_config, setup_logger
from datetime import datetime

CONFIG_FILE = "config.yaml"


def main():
    logger = setup_logger("Main Runner", "main_runner.log")

    if os.path.exists(CONFIG_FILE):
        config = load_config(CONFIG_FILE)
    else:
        logger.error(f"Configuration file {CONFIG_FILE} not found.")
        return

    args = parse_runner_args()

    host_results_path = (
        f"../results/results_{datetime.now().strftime('%d-%m-%y %H_%M')}"
    )

    # Ensure the destination directory exists
    os.makedirs(host_results_path, exist_ok=True)

    available_runners = {
        "ollama": (
            OllamaRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "config": config,
                "language": args.language,
                "benchmark_name": args.benchmark_name,
                "models": args.models,
            },
        )
        # TODO: Add more runners here, vllm, transformers
    }

    for runner_name in args.tool:
        if runner_name in available_runners:
            Runner, kwargs = available_runners[runner_name]
            try:
                runner_instance = Runner(host_results_path, **kwargs)
                runner_instance.run_tool_test()
            except Exception as e:
                logger.error(f"Error running {runner_name}: {e}")
        else:
            logger.error(f"Unknown runner: {runner_name}")
            sys.exit(-1)

    # run_results_analyzer(host_results_path)

    # Move the log file to the results directory
    try:
        shutil.move("main_runner.log", f"{str(host_results_path)}/main_runner.log")
    except FileNotFoundError as e:
        logger.error(f"Error moving log file: {e}")


if __name__ == "__main__":
    main()
