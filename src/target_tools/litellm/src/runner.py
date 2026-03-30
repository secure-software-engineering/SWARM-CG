import json
import logging
import argparse
import re
import sys
import time
import os
import traceback
import utils
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sys import stdout
from pathlib import Path

from llm_utils import process_test_folder

ENABLE_STREAMING = False
REQUEST_TIMEOUT = 60
USE_MULTIPROCESSING_FOR_TERMINATION = True
TEMPERATURE = 0.1
MAX_WORKERS = 4  # Default number of parallel workers

# Call logger
logger = utils.setup_logger()

# Thread-safe counters and locks
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    def get(self):
        with self._lock:
            return self._value

# Thread-safe logging
log_lock = threading.Lock()

def safe_log(log_func, message):
    """Thread-safe logging wrapper"""
    with log_lock:
        log_func(message)

def safe_print(message):
    """Thread-safe print wrapper"""
    with log_lock:
        print(message)


def process_single_test(test_info):
    """Process a single test case - designed to be called in parallel"""
    test, file, model, api_base, prompt_id, language = test_info
    
    prompt_start_time = time.time()
    try:
        safe_log(logger.info, file)
        safe_log(logger.info, model)
        process_test_folder(
            file,
            model,
            api_base,
            prompt_id,
            language,
            logger=logger,
            request_timeout=REQUEST_TIMEOUT,
            temperature=TEMPERATURE,
            use_multiprocessing_for_termination=USE_MULTIPROCESSING_FOR_TERMINATION,
        )
        return {
            "success": True,
            "test": test,
            "file": file,
            "time": time.time() - prompt_start_time,
            "error": None,
            "error_type": None,
        }
    except Exception as e:
        safe_log(
            logger.info,
            f"Command returned non-zero exit status: {e} for file: {file}"
        )
        with log_lock:
            traceback.print_exc()
        
        error_type = None
        if isinstance(e, utils.JsonException):
            error_type = "json"
        elif isinstance(e, utils.TimeoutException):
            error_type = "timeout"
        
        return {
            "success": False,
            "test": test,
            "file": file,
            "time": time.time() - prompt_start_time,
            "error": e,
            "error_type": error_type,
        }


def main_runner(args):
    runner_start_time = time.time()

    for model in args.models:
        # Thread-safe counters
        error_counter = ThreadSafeCounter()
        timeout_counter = ThreadSafeCounter()
        json_counter = ThreadSafeCounter()
        files_analyzed_counter = ThreadSafeCounter()

        benchmark_path = Path(args.benchmark_path)

        results_src = benchmark_path
        if not results_src.exists():
            logger.error(f"Benchmark source path {results_src} does not exist.")
            sys.exit(-1)

        model_dir_name = model.replace("/", "_").replace(":", "_")
        if args.results_dir is None:
            results_dst = benchmark_path.parent / model_dir_name / benchmark_path.name
        else:
            results_dst = Path(args.results_dir) / model_dir_name / benchmark_path.name
            os.makedirs(results_dst, exist_ok=True)
        utils.copy_folder(results_src, results_dst)

        model_start_time = time.time()

        # Collect all test cases to process
        test_cases = []
        for cat in sorted(os.listdir(results_dst)):
            safe_print(f"Collecting tests from category {cat}...")
            tests = os.listdir(os.path.join(results_dst, cat))
            for test in tests:
                file = os.path.join(results_dst, cat, test)
                test_cases.append((test, file, model, args.api_base, args.prompt_id, args.language))
        
        safe_print(f"Processing {len(test_cases)} test cases with {args.max_workers} workers...")
        
        # Process test cases in parallel
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            # Submit all tasks
            future_to_test = {
                executor.submit(process_single_test, test_info): test_info 
                for test_info in test_cases
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_test):
                result = future.result()
                
                files_analyzed = files_analyzed_counter.increment()
                
                if not result["success"]:
                    error_counter.increment()
                    if result["error_type"] == "json":
                        json_counter.increment()
                    elif result["error_type"] == "timeout":
                        timeout_count = timeout_counter.increment()
                        if timeout_count > 10:
                            safe_log(logger.error, "Timeout threshold reached!")
                            # Cancel remaining futures
                            for f in future_to_test:
                                f.cancel()
                            break
                
                safe_log(
                    logger.info,
                    f"\n\nProgress: {files_analyzed}/{len(test_cases)} | Total Errors"
                    " / JSON Errors / Timeouts:"
                    f" {error_counter.get()},{json_counter.get()},{timeout_counter.get()} | "
                    f"TestTime: {result['time']:.2f}s | Test: {result['test']}\n\n"
                )
        
        logger.info(
            f"Model {model} finished in {time.time()-model_start_time:.2f} seconds"
        )
    logger.info(
        f"Runner finished in {time.time()-runner_start_time:.2f} seconds, with errors:"
        f" {error_counter.get()} | JSON errors: {json_counter.get()}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument Parsing for LiteLLM runner")
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
    parser.add_argument(
        "--api_base",
        help="Optional base URL for the LiteLLM proxy or custom API endpoint",
        default=None,
    )
    parser.add_argument("--prompt_id", help="Specify the prompt ID", required=True)
    parser.add_argument(
        "--models",
        nargs="+",
        type=str,
        help="Space-separated list of model names (e.g. ollama/llama3 openai/gpt-4o)",
        required=True,
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Number of parallel workers for processing test cases (default: {MAX_WORKERS})",
    )
    args = parser.parse_args()
    main_runner(args)
