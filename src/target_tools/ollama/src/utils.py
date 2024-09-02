import json
import os
import re
import shutil
import sys
import requests
import logging


def setup_logger():
    """logger for ollama callgraph runenr"""
    logger = logging.getLogger("ollama_runner")
    logger.setLevel(logging.DEBUG)

    if is_running_in_docker():
        file_handler = logging.FileHandler("/tmp/ollama_callgraph_log.log", mode="w")
    else:
        file_handler = logging.FileHandler("ollama_callgraph_log.log", mode="w")

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

        parsed_answers = {}
        pattern = re.compile(r"(\d+)\.\s*(.*)")
        lines = answers.split("\n")

        for i, line in enumerate(lines):
            # i: This variable will store the index of the current line (starting from 0).
            # line: This variable will store the actual content of the current line (a string).
            match = pattern.match(line)
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


def normalize_path(path=None):
    normalized = path.replace("\\", ".").replace("/", ".")
    return normalized.rsplit(".", 1)[0]


def best_match(key, file_map, init_file_name):
    """Find the best matching file based on the key."""
    if key in file_map:
        return file_map[key]

    # Direct match with the key as a directory name
    init_key = f"{key}.{init_file_name}"
    if init_key in file_map:
        return file_map[init_key]

    # Check if the key corresponds to a function in an __init__.py file
    parts = key.split(".")
    if len(parts) > 1:
        potential_init_key = ".".join(parts[:-1]) + f".{init_file_name}"
        if potential_init_key in file_map:
            return file_map[potential_init_key]

    # Find files where the key is a prefix or is contained within
    candidates = [f for f in file_map if key.startswith(f) or f == key]
    if len(candidates) == 1:
        return file_map[candidates[0]]
    elif len(candidates) > 1:
        # Sort candidates by similarity (longer matches are considered better)
        candidates.sort(key=lambda f: len(f), reverse=True)
        return file_map[candidates[0]]
    return None


def identify_language(file_map):
    """Identify the programming language based on file extensions."""
    extensions = {file.rsplit(".", 1)[-1] for file in file_map.values()}
    if "py" in extensions:
        return "python"
    elif "js" in extensions:
        return "javascript"
    return None


def generate_questions_from_json(json_file, test_folder, logger=None):
    """
    Generate questions based on the callgraph JSON file.

    :param json_file: Path to the callgraph.json file.
    :param test_folder: Path to the test folder containing the code files (one or more). This may have subdirectories also that contain more code files
    :param logger: Logger instance.
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
                relative_path = os.path.relpath(os.path.join(root, file), test_folder)
                normalized_name = normalize_path(relative_path)
                file_map[normalized_name] = relative_path
                # Set the default file name
                if normalized_name == "main":
                    default_file_name = file_map[normalized_name]
            except Exception as e:
                if logger:
                    logger.error(
                        f"Error processing file '{file}' in generate questions functions: {e}"
                    )
                continue
    if logger:
        logger.info(f"Files in test folder '{test_folder}' are {file_map}")

    language = identify_language(file_map)
    init_file_name = "__init__" if language == "python" else "index"

    for key in data:
        # Identify the corresponding file for this function based on the key in JSON
        file_name = best_match(key, file_map, init_file_name)

        if not file_name and default_file_name:
            file_name = default_file_name
        elif not file_name:
            # Skip if no file can be determined
            if logger:
                logger.error(f"No matching file found for key: {key} in {test_folder}")
            continue

        # Generate the question based on the identified file
        if key == normalize_path(file_name):
            # If the key is a module-level function, ask about module-level calls
            question = (
                f"What are the module-level function calls in the file '{file_name}'?"
            )
        elif f"{key}.{init_file_name}" == normalize_path(file_name):
            question = f"What are the function calls in the file '{file_name}'?"
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


class JsonException(Exception):
    pass


class TimeoutException(Exception):
    pass
