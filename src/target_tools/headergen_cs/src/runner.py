import argparse
import json
import logging
import multiprocessing
import subprocess
import time
from pathlib import Path
from sys import stdout

import requests
import translator
import utils
import os
import sys
import traceback

from headergen_utils import process_test_folder, get_hg_cs

# Create a logger
logger = logging.getLogger("runner")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("/tmp/headergen_log.log")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

MAX_RETRY_COUNT = 3


def list_python_files(folder_path):
    python_files = sorted(Path(folder_path).rglob("*.py"))
    return python_files


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

            files_analyzed += 1

    logger.info(
        f"Runner finished in {time.time()-runner_start_time:.2f} seconds, with errors:"
        f" {error_count} | JSON errors: {json_count}"
    )


def run_headergen_server():
    retry_count = 0
    while retry_count < MAX_RETRY_COUNT:
        try:
            subprocess.run(["headergen", "server"], check=True)
        except Exception as e:
            logger.info(f"Attempt {retry_count+1} failed: {e}")
            retry_count += 1


if __name__ == "__main__":
    is_running_in_docker = utils.is_running_in_docker()
    if is_running_in_docker:
        print("Python is running inside a Docker container")
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--benchmark_path",
            help="Specify the benchmark path",
            default="/tmp/micro-benchmark/",
        )

        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            server_process = multiprocessing.Process(target=run_headergen_server)
            server_process.start()
            time.sleep(10)

            args = parser.parse_args()
            main_runner(args)

            server_process.terminate()
            server_process.join()

    else:
        print("Python is not running inside a Docker container")
        file_path = "/mnt/Projects/PhD/Research/HeaderGen/git_sources/HeaderGen_github/.scrapy/test/imports/test.py"
        response = get_hg_cs(file_path)
        print(response)
