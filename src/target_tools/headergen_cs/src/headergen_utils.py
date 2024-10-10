import utils
import json
import os
import re
import time
import requests
import multiprocessing
from pathlib import Path

logger = utils.setup_logger()


# Returns language extension
def get_language_extension(language):
    """Returns the file extension for the given programming language."""
    return {"python": "py", "javascript": "js", "java": "java"}.get(language, "py")


def get_hg_cs(file_path):
    try:
        base_url = "http://0.0.0.0:54068/get_cs"
        params = {
            "file_path": str(file_path),
        }
        url = (
            base_url + "?" + "&".join(f"{key}={value}" for key, value in params.items())
        )
        print("Checking in URL:", url.strip())

        response = requests.get(url)

        return response.json()
    except Exception as e:
        logger.info(f"{file_path} failed: {e}")
        raise


# Function to process the test folder
def process_test_folder(file_folder):
    try:
        file_path = os.path.join(file_folder, f"main.py")
        result_filepath = os.path.join(file_folder, f"main_result.json")

        output = get_hg_cs(file_path)

        with open(result_filepath, "w") as file:
            file.write(json.dumps(output, indent=4))

    except Exception as e:
        logger.error(f"{file_path} failed: {e}")
        raise
