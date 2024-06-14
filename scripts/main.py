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
    REPO_ROOT = Path(__file__).parent.parent
    os.makedirs(REPO_ROOT / ".data", exist_ok=True)
    return REPO_ROOT


logger = setup_logging("main")
logger.info("Application start")


def translate_pycg(
    test_case, config, llmRunner, target_lang, filetype_suffix, source_lang="python", avoid_rate_limiting=False
):
    try:
        system_prompt_id = config["translation_prompt_system"]
        prompt_id_user = config["translation_prompt_user"]

        feature_category = test_case["feature_category"]
        description = test_case["description"]
        code = test_case["code"]
        code_call_graph = test_case["call_graph"]

        if avoid_rate_limiting:
            # sleep for a random time between 1 and 5 seconds to avoid rate limiting
            time.sleep(randint(1, 3))

        prompt_start_time = time.time()

        prompt_formatter = PromptFormatter(show_token_count=True)

        prompt = prompt_formatter.process_translation_chat_prompt(
            prompt_id_system=system_prompt_id,
            prompt_id_user=prompt_id_user,
            source_language=source_lang,
            target_language=target_lang,
            filetype_suffix=filetype_suffix,
            feature_category=feature_category,
            description=description,
            code=code,
            code_call_graph=code_call_graph,
        )
        response = llmRunner.process_prompt(prompt)
        response_formatter = ReponseFormatter()
        response = response_formatter.get_transalated_json(response)

        # response = response.replace("```json", "").replace("```", "").replace("\n", "")

        response = json.loads(response)
        passed = True

        # Dump response to file

    except Exception as e:
        logger.error(
            f"Command returned non-zero exit status: '{e}' for testcase: {test_case['feature_category']}-{test_case['test_case_folder']}"
        )
        passed = False

    return passed, response


# Main function to run the application
def main(config):

    # model = "gpt-3.5-turbo"
    model = "gpt-4-0125-preview"

    src_dir = config["pycg_path"]
    dest_dir = config["output_path"]
    
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

    # Translate PyCG
    # iterate all folders and first level folders are feature categories
    # second level folders are test cases
    # each test case has code and call graph
    for feature_category in os.listdir(src_dir):
        feature_category_path = src_dir / feature_category
        if not feature_category_path.is_dir():
            continue

        for test_case_folder in os.listdir(feature_category_path):
            test_case_folder_path = feature_category_path / test_case_folder
            if not test_case_folder_path.is_dir():
                continue

            dest_folder = dest_dir / test_case_folder_path.relative_to(src_dir)
            dest_folder.mkdir(parents=True, exist_ok=True)

            # create any dir in test_case_folder_path in dest_folder
            for root, dirs, files in os.walk(test_case_folder_path):
                for dir in dirs:
                    (dest_folder / dir).mkdir(parents=True, exist_ok=True)

            # check if README.md exists in dest_folder
            if (dest_folder / "README.md").exists():
                logger.info(f"Skipping: {feature_category} - {test_case_folder}")
                continue

            # read all .py files in the test case folder and append as string separated by ``` with filename
            for file in os.listdir(test_case_folder_path):
                if file.endswith(".py"):
                    with open(test_case_folder_path / file, "r") as f:
                        code = f.read()
                        code = f"```{file}\n{code}```\n\n"    

            #  read call graph from the test case folder
            with open(test_case_folder_path / "callgraph.json", "r") as f:
                call_graph = f.read()
                call_graph = f"```\n{call_graph}```"


            # read README.md for description
            description_path = test_case_folder_path / "README.md"
            with open(description_path, "r") as f:
                description = f.read()

            test_case = {
                "feature_category": feature_category,
                "test_case_folder": test_case_folder,
                "description": description,
                "code": code,
                "call_graph": call_graph,
            }

            passed, response = translate_pycg(
                test_case=test_case,
                config=config,
                llmRunner=llmRunner,
                target_lang="java",
                filetype_suffix="java",
                source_lang="python",
                avoid_rate_limiting=False,
            )

            if passed:
                translated_code = response["translated_code"]
                translated_call_graph = json.loads(response["call_graph"])

                # save translated code with new filenames according to json and call graph to the destination folder
                for file, code in translated_code.items():
                    with open(dest_folder / file, "w") as f:
                        f.write(code)

                with open(dest_folder / "callgraph.json", "w") as f:
                    f.write(json.dumps(translated_call_graph, indent=4))

            else:
                logger.error(f"Error occurred while translating: {test_case_folder}")
                # save translated code with new filenames according to json and call graph to the destination folder
                with open(dest_folder / "response_dump", "w") as f:
                    f.write(response)

                with open(dest_folder / "callgraph.json", "w") as f:
                    f.write(response)

            with open(dest_folder / "README.md", "w") as f:
                f.write(description)

            logger.info(f"Translated: {feature_category} - {test_case_folder}")

    


if __name__ == "__main__":
    start_time = time.time()
    REPO_ROOT = init_environment()

    # TODO: Add argparse to pass the configuration file
    default_run_id = "pycg_java"

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--run_id",
        type=str,
        help="Run ID for the current run",
        default=default_run_id,
    )

    args = parser.parse_args()

    config = {
        "run_id": args.run_id,
        "use_chat": True,
        "run_parallel": False,
        "ollama_url": os.getenv("OLLAMA_URL"),
        "openai_key": os.getenv("OPENAI_API_KEY"),
        "pycg_path": REPO_ROOT / "benchmarks/python/pycg",
        "translation_prompt_system": "translation_prompt_system",
        "translation_prompt_user": "translation_prompt_user",
        "output_path": REPO_ROOT / ".data" / args.run_id,
    }

    main(config)


    logger.info(f"Total time taken: {time.time() - start_time} seconds")
