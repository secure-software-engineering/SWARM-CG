import json
import os
import shutil
import sys
import logging

TOOL = "jelly"


def setup_logger(logger_name=f"{TOOL}_runner"):
    """logger for jelly runner"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers to prevent adding duplicate ones
    if not logger.handlers:
        if is_running_in_docker():
            file_handler = logging.FileHandler(f"/tmp/{TOOL}.log", mode="w")
        else:
            file_handler = logging.FileHandler(f"{TOOL}.log", mode="w")

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


class JsonException(Exception):
    pass


class TimeoutException(Exception):
    pass
