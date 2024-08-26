import json
import logging
import argparse
import re
import sys
import time
import os
import traceback
import yaml
import utils
import multiprocessing
from sys import stdout
from pathlib import Path
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.output_parsers import OutputFixingParser

# Import functions from llm_utils
from llm_utils import process_test_folder, is_ollama_online

AUTOFIX_WITH_OPENAI = False
ENABLE_STREAMING = True
REQUEST_TIMEOUT = 60
USE_MULTIPROCESSING_FOR_TERMINATION = True

# Call logger
logger = utils.setup_logger()


def main_runner(args):
    temperature = 0.1
    runner_start_time = time.time()

    # Iterate through each model in ollama
    for model in args.ollama_models:
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

        # Determine the path for results_dst
        if args.results_dir is None:
            results_dst = benchmark_path.parent / model / benchmark_path.name
        else:
            results_dst = Path(args.results_dir) / model / benchmark_path.name
            os.makedirs(results_dst, exist_ok=True)
        utils.copy_folder(results_src, results_dst)

        if not model.startswith(("gpt-", "ft:gpt-")):
            if is_ollama_online(args.ollama_url):
                logger.info("Ollama is online!")
                llm = Ollama(
                    model=model,
                    timeout=REQUEST_TIMEOUT,
                )
                llm.base_url = args.ollama_url
                llm.invoke("Dummy prompt. limit your response to 1 letter.")
            else:
                logger.error("Ollama server is not online!!!")
                # sys.exit(-1)
        model_start_time = time.time()

        # Iterating through each category in a language
        for cat in sorted(os.listdir(results_dst)):
            print("Iterating category {}...".format(cat))
            files_analyzed = 0
            tests = os.listdir(os.path.join(results_dst, cat))

            # Iterating through each test in a category
            for test in tests:
                print(f"Running {test}...")
                file = os.path.join(results_dst, cat, test)
                # if model.startswith(("gpt-", "ft:gpt-")):
                #     # OpenAI models
                #     if "instruct" in model:
                #         pass
                #         # llm = OpenAI(
                #         #     model_name=model,
                #         #     temperature=temperature,
                #         #     openai_api_key=args.openai_key,
                #         # )
                #     else:
                #         pass
                #         # llm = ChatOpenAI(
                #         #     model_name=model,
                #         #     temperature=temperature,
                #         #     openai_api_key=args.openai_key,
                #         # )
                # else:
                llm = Ollama(
                    model=model,
                    callback_manager=(
                        CallbackManager([StreamingStdOutCallbackHandler()])
                        if ENABLE_STREAMING
                        else None
                    ),
                    temperature=temperature,
                    timeout=REQUEST_TIMEOUT,
                )
                llm.base_url = args.ollama_url
                prompt_start_time = time.time()
                try:
                    logger.info(file)
                    logger.info(model)
                    process_test_folder(
                        file,
                        llm,
                        None,
                        args.prompt_id,
                        args.language,
                        logger=logger,
                        request_timeout=REQUEST_TIMEOUT,
                        autofix_with_openai=AUTOFIX_WITH_OPENAI,
                        use_multiprocessing_for_termination=USE_MULTIPROCESSING_FOR_TERMINATION,
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
                    f"\n\nProgress: {files_analyzed} | Total Errors"
                    " / JSON Errors / Timeouts:"
                    f" {error_count},{json_count},{timeout_count} | PromptTime:"
                    f" {time.time()-prompt_start_time}\n\n"
                )
        logger.info(
            f"Model {model} finished in {time.time()-model_start_time:.2f} seconds"
        )
        # logger.info(
        #     "Running translator"
        # )
        # translator.main_translator(results_dst)
    logger.info(
        f"Runner finished in {time.time()-runner_start_time:.2f} seconds, with errors:"
        f" {error_count} | JSON errors: {json_count}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument Parsing for Ollama runner")
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
        "--ollama_url", help="Specify the ollama server url", required=True
    )
    parser.add_argument("--prompt_id", help="Specify the prompt ID", required=True)
    parser.add_argument(
        "--ollama_models",
        nargs="+",
        type=str,
        help="Space-separated list of ollama models",
        required=True,
    )
    parser.add_argument("--openai_key", help="Openai API key", required=True)
    args = parser.parse_args()
    main_runner(args)
