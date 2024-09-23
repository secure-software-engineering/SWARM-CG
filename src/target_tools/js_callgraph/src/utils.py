import json
import os
import re
import shutil
import sys
import logging

TOOL = "js_callgraph"


def setup_logger(logger_name=f"{TOOL}_runner"):
    """logger for js_callgraph runner"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers to prevent adding duplicate ones
    if not logger.handlers:
        if is_running_in_docker():
            file_handler = logging.FileHandler(
                f"/tmp/{TOOL}_js_callgraph.log", mode="w"
            )
        else:
            file_handler = logging.FileHandler(f"{TOOL}_js_callgraph.log", mode="w")

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

        parsed_answers = []
        pattern = re.compile(r"(\d+)\.\s*(.*)")
        lines = answers.split("\n")
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                parsed_answers.append(match.groups())
            else:
                parsed_answers.append((i, ""))

        if not parsed_answers:
            parsed_answers = [(0, answers)]

        answers_json_data = {}
        for i, line_number in enumerate(gt_data):
            if (i + 1) <= len(parsed_answers):
                if parsed_answers[i][1] == "":
                    answers_json_data[line_number] = []
                else:
                    answers_json_data[line_number] = [
                        x.strip() for x in parsed_answers[i][1].split(",")
                    ]

        return answers_json_data
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
    for fact in sorted(data):
        if fact == "main":
            answers.append(f"{counter}. {', '.join(data['main'])}")
        else:
            answers.append(f"{counter}. {', '.join(data[fact])}")

        counter += 1

    return "\n".join(answers)


def generate_questions_from_json(json_file, file_name="main.py"):
    # Read and parse the JSON file
    with open(json_file, "r") as file:
        data = json.load(file)

    questions = []
    for key in sorted(data):
        if file_name.split(".")[0] == key:
            question = (
                f"What are the module level function calls in the file '{file_name}'?"
            )
        else:
            question = (
                f"What are the function calls inside the '{key}' function in the"
                f" file '{file_name}'?"
            )

        questions.append(question)

    if len(data) != len(questions):
        print("ERROR! Type questions length does not match json length")
        sys.exit(-1)

    questions = [f"{x}. {y}" for x, y in zip(range(1, len(questions) + 1), questions)]
    return questions


class JsonException(Exception):
    pass


class TimeoutException(Exception):
    pass
