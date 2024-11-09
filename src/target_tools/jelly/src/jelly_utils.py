import logging
import json
import os
import subprocess
from translator import convert_jelly_to_swarm

logger = logging.getLogger("jelly_runner")


def get_jelly_cg(test_folder, file_path):
    try:
        print(f"Processing test folder: {test_folder}")
        if not os.path.exists(file_path):
            print(f"main.js not found in {test_folder}")
            return

        command_to_run = [
            "jelly",
            "-j",
            file_path.replace(".js", ".json"),
            "--approx",
            test_folder,
            "-b",
            test_folder,
        ]

        result = subprocess.run(
            command_to_run,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        # Check if the command was successful
        cg = {}
        if result.returncode == 0:
            print("Command Output:\n", result.stdout)
            with open(file_path.replace(".js", ".json"), "r") as file:
                cg_json = json.load(file)
                cg = convert_jelly_to_swarm(test_folder, cg_json)
        else:
            logger.error("Command Failed with return code", result.returncode)
            print("Error Output:\n", result.stderr)
            logger.error(f"Error Output in {file_path}: {result.stderr}")
            raise Exception(f"Error processing {file_path}")
    except FileNotFoundError:
        print("Error: The specified file was not found.")
        logger.error("Error: The specified file was not found.")
    except Exception as e:
        logger.error(f"Error running js_callgraph test: {e}")
        raise Exception(f"Error processing {file_path}")
    return json.dumps(cg, indent=4)


def process_test_folder(test_folder):
    try:
        file_path = os.path.join(test_folder, f"main.js")
        result_filepath = os.path.join(test_folder, f"main_result.json")

        output = get_jelly_cg(test_folder, file_path)

        with open(result_filepath, "w") as file:
            file.write(output)
    except Exception as e:
        logger.error(f"{file_path} failed: {e}")
        raise
