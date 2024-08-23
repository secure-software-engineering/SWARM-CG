import utils
import json
import os
import re
import time
import requests
import multiprocessing
from pycg import pycg
from pycg import formats
from pathlib import Path

logger = utils.setup_logger()


# Returns language extension
def get_language_extension(language):
    """Returns the file extension for the given programming language."""
    return {"python": "py", "javascript": "js", "java": "java"}.get(language, "py")


def get_pycg_cg(file_path):
    cg = pycg.CallGraphGenerator(
        [file_path], str(Path(file_path).parent), -1, "call-graph"
    )
    cg.analyze()

    formatter = formats.Simple(cg)

    cg_json = formatter.generate()

    return json.dumps(cg_json, indent=4)


# Function to process the test folder
def process_test_folder(file_folder):
    try:
        file_path = os.path.join(file_folder, f"main.py")
        result_filepath = os.path.join(file_folder, f"main_result.json")

        output = get_pycg_cg(file_path)

        with open(result_filepath, "w") as file:
            file.write(output)

    except Exception as e:
        logger.error(f"{file_path} failed: {e}")
        raise
