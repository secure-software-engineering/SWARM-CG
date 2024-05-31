import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from random import randint

import utils
import utils.exceptions
from dotenv import load_dotenv
from llm.llm_runner import LLMRunner
from llm.prompt_formatter import PromptFormatter
from llm.response_formatter import ReponseFormatter
from utils.setup_logging import setup_logging


# Initialize global variables and environment
def init_environment():
    ENV_FILE = Path(__file__).parent.parent / ".env"
    load_dotenv(ENV_FILE)
    REPO_ROOT = Path(__file__).parent.parent.parent
    os.makedirs(REPO_ROOT / ".data", exist_ok=True)
    return REPO_ROOT


logger = setup_logging("main")
logger.info("Application start")

# Main function to run the application
def main(run_id, run_on_obfuscated):
    REPO_ROOT = init_environment()

    model = "gpt-3.5-turbo"

    try:
        llmRunner = LLMRunner(
            model=model,
            openai_key=config["openai_key"],
            ollama_url=config["ollama_url"],
            enable_chat=config["use_chat"],
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLMRunner for model {model}: {e}")
        return None

    if model.startswith(("gpt-", "ft:gpt-")):
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_test_case = {
                executor.submit(
                    classify_test_case_func,
                    test_case,
                    config,
                    cache_file_paths,
                    llmRunner,
                    True,
                ): test_case
                for test_case in test_cases
            }
            total_test_cases = len(test_cases)
            completed_test_cases = 0

            for future in as_completed(future_to_test_case):
                test_case_name, result = future.result()
                test_case = future_to_test_case[future]
                test_case["classification"] = result
                completed_test_cases += 1
                logger.info(
                    f"Processed {completed_test_cases}/{total_test_cases}: {test_case_name}"
                )
    else:
        total_test_cases = len(test_cases)
        for index, test_case in enumerate(test_cases, start=1):
            test_case["classification"] = classify_test_case_func(
                test_case, config, cache_file_paths, llmRunner
            )[1]
            logger.info(f"Processed {index}/{total_test_cases}: {test_case['name']}")


if __name__ == "__main__":
    start_time = time.time()
    # TODO: Add argparse to pass the configuration file
    default_run_id = "Rerun_failed_tests_gpt4"

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run_id",
        type=str,
        help="Run ID for the current run",
        default=default_run_id,
    )
    parser.add_argument(
        "--run_on_obfuscated",
        type=bool,
        help="Run on obfuscated code",
        default=False,
    )

    args = parser.parse_args()

    main(args.run_id, False)

    if args.run_on_obfuscated:
        logger.info("Running on obfuscated code")
        main(f"{args.run_id}_obfuscated", True)

    logger.info(f"Total time taken: {time.time() - start_time} seconds")
