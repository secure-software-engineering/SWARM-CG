import json
import os
import re
import shutil
import sys
import requests
import logging

import prompts
import copy
import yaml


def is_running_in_docker():
    """Check if Python is running inside a Docker container."""
    return (
        os.path.exists("/.dockerenv")
        or os.environ.get(  # Check if the /.dockerenv file exists
            "DOCKER_CONTAINER", False
        )
        or os.environ.get(  # Check if DOCKER_CONTAINER environment variable is set
            "DOCKER_IMAGE_NAME", False
        )  # Check if DOCKER_IMAGE_NAME environment variable is set
    )


def setup_logger():
    """logger for ollama callgraph runenr"""
    logger = logging.getLogger("llm_runner")
    logger.setLevel(logging.DEBUG)

    if is_running_in_docker():
        file_handler = logging.FileHandler("/tmp/llm_callgraph_log.log", mode="w")
    else:
        file_handler = logging.FileHandler("llm_callgraph_log.log", mode="w")

    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Call logger
logger = setup_logger()


class JsonException(Exception):
    pass


class TimeoutException(Exception):
    pass


def is_running_in_docker():
    """Check if Python is running inside a Docker container."""
    return (
        os.path.exists("/.dockerenv")
        or os.environ.get(  # Check if the /.dockerenv file exists
            "DOCKER_CONTAINER", False
        )
        or os.environ.get(  # Check if DOCKER_CONTAINER environment variable is set
            "DOCKER_IMAGE_NAME", False
        )  # Check if DOCKER_IMAGE_NAME environment variable is set
    )


def copy_folder(src, dst):
    """
    Copies a folder from the source (src) to the destination (dst).

    :param src: Source folder path
    :param dst: Destination folder path
    """
    # Check if the source directory exists
    if not os.path.exists(src):
        print(f"Source folder {src} does not exist.")
        return

    # Check if the destination directory exists, if so, remove it
    if os.path.exists(dst):
        shutil.rmtree(dst)
        print(f"Existing folder at {dst} has been removed.")

    # Copy the folder
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"Folder copied from {src} to {dst}")


def generate_json_file(filename, type_info):
    # Generate JSON file with type information
    try:
        if isinstance(type_info, dict):
            pass
        else:
            type_info = json.loads(type_info)
        is_valid_json = True
    except Exception as e:
        is_valid_json = False
        print(f"Not a valid JSON: {e}")

    json_data = json.dumps(type_info, indent=4)
    with open(filename, "w") as file:
        file.write(json_data)

    return is_valid_json


def generate_json_from_answers(gt_json_file, answers):
    try:
        with open(gt_json_file, "r") as file:
            gt_data = json.load(file)

        parsed_answers = {}
        pattern = re.compile(r"(\d+)\.\s*(.*)")
        lines = answers.split("\n")

        for i, line in enumerate(lines):
            # i: This variable will store the index of the current line (starting from 0).
            # line: This variable will store the actual content of the current line (a string).
            match = pattern.match(line.strip())
            if match:
                # parsed_answers.append(match.groups())
                question_number, answer_text = match.groups()
                parsed_answers[int(question_number)] = answer_text
            # else:
            #     parsed_answers.append((i, ""))
        # Initialize the answers JSON structure based on gt_data
        answers_json_data = {key: [] for key in gt_data.keys()}

        # Map parsed answers to gt_data keys
        for i, (gt_key, _) in enumerate(gt_data.items(), start=1):
            if i in parsed_answers:
                answer = parsed_answers[i]
                if answer.strip() == "":
                    answers_json_data[gt_key] = []
                else:
                    answers_json_data[gt_key] = [x.strip() for x in answer.split(",")]
            else:
                answers_json_data[gt_key] = []

        return answers_json_data

        # if not parsed_answers:
        #     parsed_answers = [(0, answers)]

        # answers_json_data = {}
        # for i, line_number in enumerate(gt_data):
        #     if (i + 1) <= len(parsed_answers):
        #         if parsed_answers[i][1] == "":
        #             answers_json_data[line_number] = []
        #         else:
        #             answers_json_data[line_number] = [
        #                 x.strip() for x in parsed_answers[i][1].split(",")
        #             ]

        # return answers_json_data
    except Exception as e:
        print("Error generating json from questions")
        print(e)
        return []


def generate_answers_for_fine_tuning(json_file):
    # Read and parse the JSON file
    with open(json_file, "r") as file:
        data = json.load(file)

    questions = generate_questions_from_json(json_file)
    for i, q in enumerate(questions):
        if "module" in q:
            module_q = i + 1

    counter = 1
    answers = []
    for fact in data:
        if fact == "main":
            answers.append(f"{counter}. {', '.join(data['main'])}")
        else:
            answers.append(f"{counter}. {', '.join(data[fact])}")

        counter += 1

    return "\n".join(answers)


def generate_questions_from_json(json_file, test_folder):
    """
    Generate questions based on the callgraph JSON file.

    :param json_file: Path to the callgraph.json file.
    :param test_folder: Path to the test folder containing code files.
    :param logger: Logger instance for logging information.
    :return: A list of generated questions.
    """

    questions = []
    file_map = {}
    default_file_name = None

    try:
        # Read and parse the JSON file
        with open(json_file, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if logger:
            logger.error(f"Failed to read or parse JSON file '{json_file}': {e}")
        return questions

    # Walk through the test_folder to gather all code files
    for root, _, files in os.walk(test_folder):
        for file in files:
            try:
                # Get the base name of the file (without extension) and store it in the map
                file_base_name = os.path.splitext(file)[0]
                file_map[file_base_name] = os.path.relpath(
                    os.path.join(root, file), test_folder
                )
                # Set the default file name
                if file_base_name == "main":
                    default_file_name = file_map[file_base_name]
            except Exception as e:
                if logger:
                    logger.error(
                        f"Error processing file '{file}' in generate questions functions: {e}"
                    )
                continue

    if logger:
        logger.info(f"Files in test folder '{test_folder}' are {file_map}")

    for key in data:
        # Identify the corresponding file for this function based on the key in JSON
        file_name = None

        # If the key directly matches a file base name, use that file
        if key in file_map:
            file_name = file_map[key]
        else:
            # If the key doesn't match directly, find files where the key is a prefix
            matching_files = [f for f in file_map if key.startswith(f)]
            if len(matching_files) == 1:
                file_name = file_map[matching_files[0]]
            elif len(matching_files) > 1:
                # TODO: this needs to be updated
                matching_files.sort(key=lambda f: len(f), reverse=True)
                file_name = file_map[matching_files[0]]
            else:
                # If no matching files, use the default file name (main.py or main.js)
                if default_file_name:
                    file_name = default_file_name
                else:
                    # Skip if no file can be determined
                    if logger:
                        logger.error(
                            f"No matching file found for key: {key} in {test_folder}"
                        )
                    continue

        # Generate the question based on the identified file
        if key == os.path.splitext(os.path.basename(file_name))[0]:
            # If the key is a module-level function, ask about module-level calls
            question = (
                f"What are the module-level function calls in the file '{file_name}'?"
            )
        else:
            # Otherwise, ask about the function calls inside a specific function
            question = f"What are the function calls inside the '{key}' function in the file '{file_name}'?"

        questions.append(question)

    # Check if the number of questions matches the entries in the JSON data
    if len(data) != len(questions):
        if logger:
            logger.error(
                f"ERROR! Number of questions ({len(questions)}) does not match JSON entries ({len(data)}) for '{test_folder}'"
            )
        else:
            print(
                f"ERROR! Number of questions ({len(questions)}) does not match JSON entries ({len(data)}) for '{test_folder}'"
            )
        return []

    # Number the questions for clarity
    questions = [f"{x}. {y}" for x, y in zip(range(1, len(questions) + 1), questions)]

    if logger:
        logger.info(
            f"{len(questions)} questions generated for test folder '{test_folder}'."
        )

    return questions


def load_models_config(config_path):
    models_config = {"models": {}, "custom_models": {}, "openai_models": {}}
    with open(config_path, "r") as file:
        config_data = yaml.safe_load(file)
        for model_data in config_data["models"]:
            models_config["models"][model_data["name"]] = model_data
        for model_data in config_data["custom_models"]:
            models_config["custom_models"][model_data["name"]] = model_data
        for model_data in config_data["openai_models"]:
            models_config["openai_models"][model_data["name"]] = model_data

    return models_config


def load_runner_config(config_path):
    with open(config_path, "r") as file:
        config_data = yaml.safe_load(file)

    return config_data["runner_config"]


def get_language_extension(language):
    """
    Returns the file extension for the given programming language.
    """
    return {"python": "py", "javascript": "js", "java": "java"}.get(language, "py")


# Function to gather code files from each test folder
def gather_code_files_from_test_folder(test_folder, language_extension):
    """Recursively gathers all code files with the specified language extension."""
    code_files = []
    for root, _, files in os.walk(test_folder):
        for file in files:
            if file.endswith(f".{language_extension}"):
                code_files.append(os.path.join(root, file))
    return code_files


def get_prompt(
    prompt_id,
    file_path,
    answers_placeholders=True,
    use_system_prompt=True,
    language=None,
):
    json_filepath = os.path.join(file_path, "callgraph.json")
    extension = get_language_extension(language)

    code_files = gather_code_files_from_test_folder(file_path, extension)

    # Concatenate code contents
    code = ""
    for code_file in code_files:
        with open(code_file, "r") as file:
            code_content = file.read()
            relative_path = os.path.relpath(code_file, file_path)
            # Add filename to the code content for context
            code += f"```{relative_path}\n{code_content}```\n\n"

    # Remove comments from code but keep line number structure
    code = "\n".join(
        [line if not line.startswith("#") else "#" for line in code.split("\n")]
    )

    if prompt_id in [
        "prompt_template_questions_based_1",
    ]:
        questions_from_json = generate_questions_from_json(json_filepath, file_path)

        prompt_data = {
            "code": code,
            "questions": "\n".join(questions_from_json),
            "answers": (
                "\n".join([f"{x}." for x in range(1, len(questions_from_json) + 1)])
                if answers_placeholders
                else ""
            ),
            "language": language.capitalize(),
        }

        if use_system_prompt:
            prompt = copy.deepcopy(eval(f"prompts.{prompt_id}"))
            prompt[1]["content"] = prompt[1]["content"].format(**prompt_data)
        else:
            prompt = copy.deepcopy(eval(f"prompts.{prompt_id}_no_sys"))
            prompt[0]["content"] = prompt[0]["content"].format(**prompt_data)

    else:
        logger.error("ERROR! Prompt not found!")
        sys.exit(-1)

    return prompt


# Example usage:
# loader = ConfigLoader("models_config.yaml")
# loader.load_config()
# models = loader.get_models()
# for model in models:
#     print(model.name, model.model_path)
