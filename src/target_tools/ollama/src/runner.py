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

AUTOFIX_WITH_OPENAI = False
ENABLE_STREAMING = True
REQUEST_TIMEOUT = 60
USE_MULTIPROCESSING_FOR_TERMINATION = True

# Call logger
logger = utils.setup_logger()

# Benchmark configuration details
BENCHMARK_MAP = {
    "python": "python/pycg",
    "javascript": "javascript/pycg_js",
    "java": "java/cats"
}

def invoke_llm(llm, prompt, queue):
    try:
        output = llm.invoke(prompt)
        queue.put(output)
    except Exception as e:
        queue.put(e)

def get_prompt(prompt_id, code_path, json_filepath, answers_placeholders=True):
    # with open(json_filepath, "r") as file:
    #     data = json.load(file)
    with open(code_path, "r") as file:
        code = file.read()
        # Remove comments from code but keep line number structure
        code = "\n".join(
            [line if not line.startswith("#") else "#" for line in code.split("\n")]
        )

    if prompt_id in [
        "questions_based_1",
    ]:
        questions_from_json = utils.generate_questions_from_json(json_filepath)
        prompt_template = eval(f"prompts.{prompt_id}")

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["code", "questions", "answers"],
        )

        prompt_data = {
            "code": code,
            "questions": "\n".join(questions_from_json),
            "answers": (
                "\n".join([f"{x}." for x in range(1, len(questions_from_json) + 1)])
                if answers_placeholders
                else ""
            ),
        }
    else:
        logger.error("ERROR! Prompt not found!")
        sys.exit(-1)
    _input = prompt.format_prompt(**prompt_data)

    return _input.to_string()

def process_file(file_path, llm, openai_llm, prompt_id):
    file_start_time = time.time()
    try:
        code_filepath = os.path.join(file_path, "main.py")
        json_filepath = os.path.join(file_path, "callgraph.json")
        result_filepath = os.path.join(file_path, f"main_result.json")
        result_dump_filepath = os.path.join(file_path, f"response_dump.txt")

        if USE_MULTIPROCESSING_FOR_TERMINATION:
            # Queue for communication between processes
            queue = multiprocessing.Queue()

            # Create a process for llm.invoke
            process = multiprocessing.Process(
                target=invoke_llm,
                args=(llm, get_prompt(prompt_id, code_filepath, json_filepath), queue),
            )
            process.start()

            # Wait for the process to finish with a timeout (e.g., 60 seconds)
            process.join(timeout=REQUEST_TIMEOUT)

            if process.is_alive():
                logger.info(f"Timeout occurred for {code_filepath}")
                process.terminate()  # Terminate the process if it's still running
                process.join()
                logger.info(f"{code_filepath} failed: Not a valid JSON")
                raise utils.TimeoutException("json")

            result = queue.get_nowait()

            if isinstance(result, Exception):
                raise result

            output = result
        else:
            output = llm.invoke(get_prompt(prompt_id, code_filepath, json_filepath))

        # if isinstance(llm, ChatOpenAI):
        #     output = output.content

        with open(result_dump_filepath, "w") as file:
            file.write(output)

        # TODO: Include this in langchain pipeline
        output = re.sub(r"```json", "", output)
        output = re.sub(r"```", "", output)

        if AUTOFIX_WITH_OPENAI:
            new_parser = OutputFixingParser.from_llm(parser=parser, llm=openai_llm)
            output = new_parser.parse(output)

        logger.info(
            "File processed for model"
            f" {llm.model if getattr(llm, 'model', False) else llm.model_name} finished"
            f" in: {time.time()-file_start_time:.2f}"
        )

    except Exception as e:
        # traceback.print_exc()
        logger.error(f"{code_filepath} failed: {e}")
        raise

    logger.info(output)

    # TODO: Improve the way this is done. Some plugin based design.
    if prompt_id in ["questions_based_1"]:
        translated_json = utils.generate_json_from_answers(json_filepath, output)
    else:
        translated_json = output

    is_valid_json = utils.generate_json_file(result_filepath, translated_json)
    if not is_valid_json:
        logger.info(f"{code_filepath} failed: Not a valid JSON")
        raise utils.JsonException("json")

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
        if args.language in BENCHMARK_MAP:
            language_path = BENCHMARK_MAP[args.language]
        else:
            logger.error(f"Unsupported language: {args.language}")
            sys.exit(-1)
        results_src = Path(benchmark_path) / language_path
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
            if utils.is_ollama_online(args.ollama_url):
                logger.info("Ollama is online!")
                llm = Ollama(
                    model=model,
                    timeout=REQUEST_TIMEOUT,
                )
                llm.base_url = args.ollama_url
                llm.invoke("Dummy prompt. limit your response to 1 letter.")
            else:
                logger.error("Ollama server is not online!!!")
                sys.exit(-1)
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
                    process_file(file, llm, None, args.prompt_id)
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
        help="Language setting for the runner"
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
        "--ollama_url", 
        help="Specify the ollama server url",
        required=True
    )
    parser.add_argument(
        "--prompt_id", 
        help="Specify the prompt ID",
        required=True
    )
    parser.add_argument(
        "--ollama_models",
        nargs="+",
        type=str,
        help="Space-separated list of ollama models",
        required=True
    )
    parser.add_argument(
        "--openai_key", 
        help="Openai API key",
        required=True
    )
    args = parser.parse_args()
    main_runner(args)