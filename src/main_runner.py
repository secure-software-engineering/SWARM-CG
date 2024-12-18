import os
import shutil
import sys

# TODO: could be dynamically imported
from result_analysis.utils import run_results_analyzer
from runners import (
    OllamaRunner,
    PyCGRunner,
    LLMRunner,
    HeaderGenCSRunner,
    TAJSRunner,
    JsCallgraphRunner,
    JellyRunner,
)
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
        ),
        "pycg": (
            PyCGRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "config": config,
                "benchmark_name": args.benchmark_name,
                "language": args.language,
            },
        ),
        "llms": (
            LLMRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "benchmark_name": args.benchmark_name,
                "language": args.language,
                "config": config,
            },
        ),
        "headergen_cs": (
            HeaderGenCSRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "config": config,
                "benchmark_name": args.benchmark_name,
                "language": args.language,
            },
        ),
        "tajs": (
            TAJSRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "config": config,
                "benchmark_name": args.benchmark_name,
                "language": args.language,
            },
        ),
        "js_callgraph": (
            JsCallgraphRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "config": config,
                "benchmark_name": args.benchmark_name,
                "language": args.language,
            },
        ),
        "jelly": (
            JellyRunner,
            {
                "debug": args.debug,
                "nocache": args.nocache,
                "config": config,
                "benchmark_name": args.benchmark_name,
                "language": args.language,
            },
        ),
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

    # run_results_analyzer(host_results_path, args.language)

    # Move the log file to the results directory
    try:
        shutil.move("main_runner.log", f"{str(host_results_path)}/main_runner.log")
    except FileNotFoundError as e:
        logger.error(f"Error moving log file: {e}")


# def run_results_analyzer(results_dir, language):
#     """
#     Runs the main_analyze_result.py script with the required arguments.

#     :param results_dir: Path to the directory containing the results.
#     :param language: The language to analyze (passed as an argument).
#     """

#     analyzer_script = os.path.join(os.path.dirname(__file__), "main_analyze_result.py")

#     try:
#         # Running the script using subprocess
#         subprocess.run(
#             [
#                 sys.executable,  # Python interpreter
#                 analyzer_script,  # Path to the analysis script
#                 "--results_dir",
#                 results_dir,  # Passing the results directory
#                 "--language",
#                 language,  # Passing the language
#             ],
#             check=True,  # Raises an exception if the command fails
#         )
#         logger.info(
#             f"Successfully ran analysis on results in {results_dir} for {language}"
#         )
#     except subprocess.CalledProcessError as e:
#         logger.error(f"Error running result analysis: {e}")

if __name__ == "__main__":
    main()
