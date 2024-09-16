import argparse
import sys
import time
import os
import traceback
import utils
from pathlib import Path

from pycg_utils import process_test_folder

# Call logger
logger = utils.setup_logger()

# Benchmark configuration details
# TODO: move to the main_runner.py
BENCHMARK_MAP = {
    "python": "python/pycg",
    "javascript": "javascript/swarm_js",
    "java": "java/cats",
}


def main_runner(args):
    runner_start_time = time.time()

    error_count = 0
    timeout_count = 0
    json_count = 0

    # Create result folder for model specific results
    benchmark_path = Path(args.benchmark_path)

    # Determine the language-specific path for results_src from config
    results_src = benchmark_path
    if not results_src.exists():
        logger.error(f"Benchmark source path {results_src} does not exist.")
        sys.exit(-1)

    results_dst = results_src
    # Determine the path for results_dst
    # if args.results_dir is None:
    #     results_dst = benchmark_path.parent / benchmark_path.name
    # else:
    #     results_dst = Path(args.results_dir) / benchmark_path.name
    #     os.makedirs(results_dst, exist_ok=True)
    # utils.copy_folder(results_src, results_dst)

    # Iterating through each category in a language
    for cat in sorted(os.listdir(results_dst)):
        print("Iterating category {}...".format(cat))
        files_analyzed = 0
        tests = os.listdir(os.path.join(results_dst, cat))

        # Iterating through each test in a category
        for test in tests:
            print(f"Running {test}...")
            file = os.path.join(results_dst, cat, test)
            try:
                logger.info(file)
                process_test_folder(
                    file,
                )
            except Exception as e:
                logger.info(
                    f"Command returned non-zero exit status: {e} for file: {file}"
                )
                traceback.print_exc()

                error_count += 1
                if isinstance(e, utils.JsonException):
                    json_count += 1
                elif isinstance(e, utils.TimeoutException):
                    timeout_count += 1
                    if timeout_count > 10:
                        logger.error("Timeout threshold reached!")
                        break
            files_analyzed += 1

    logger.info(
        f"Runner finished in {time.time()-runner_start_time:.2f} seconds, with errors:"
        f" {error_count} | JSON errors: {json_count}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument Parsing for PyCG runner")
    parser.add_argument(
        "--language",
        choices=["python", "java", "javascript"],
        required=True,
        default="python",
        help="Language setting for the runner",
    )
    parser.add_argument(
        "--benchmark_path",
        help="Path to the benchmark directory",
        default="/tmp/benchmarks",
    )
    parser.add_argument(
        "--results_dir",
        help="Directory to store results",
        default=None,
    )

    args = parser.parse_args()
    main_runner(args)

# example run with arguments
