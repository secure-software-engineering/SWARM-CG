import argparse
import shutil
import sys
import time
import os
import traceback
import utils
from pathlib import Path
from jelly_utils import process_test_folder

# Call logger
logger = utils.setup_logger()


def main_runner(args):
    runner_start_time = time.time()
    error_count = 0
    timeout_count = 0
    json_count = 0
    files_analyzed = 0

    # Create result folder for model specific results
    results_src = Path(args.benchmark_path)
    if not results_src.exists():
        logger.error(f"Benchmark source path {results_src} does not exist.")
        sys.exit(-1)

    if args.results_dir is None:
        results_dst = results_src
    else:
        results_dst = Path(args.results_dir) / "jelly" / "benchmarks"
        os.makedirs(results_dst, exist_ok=True)
        utils.copy_folder(results_src, results_dst)

    # Iterating through each category in a language
    for cat in sorted(os.listdir(results_dst)):
        print("Analyzing category: {}...".format(cat))
        logger.info(f"Analyzing category: {cat}")

        tests = os.listdir(os.path.join(results_dst, cat))

        # Iterating through each test in a category
        for test in tests:
            file = os.path.join(results_dst, cat, test)
            try:
                process_test_folder(file)
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
    logger.info(f"Number of files analyzed: {files_analyzed}")

    # Move log file to the results directory
    try:
        if utils.is_running_in_docker():
            shutil.move(
                f"/tmp/js_callgraph_js_callgraph.log",
                f"{str(results_dst)}/js_callgraph_js_callgraph.log.log",
            )
    except FileNotFoundError as e:
        logger.error(f"Error moving log file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument Parsing for PyCG runner")
    parser.add_argument(
        "--language",
        choices=["javascript"],
        required=True,
        default="javascript",
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
