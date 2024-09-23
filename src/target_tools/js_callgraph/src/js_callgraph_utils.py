import utils
import json
import os
import subprocess
from translator import convert_js_callgraph

logger = utils.setup_logger()


# Returns language extension
def get_language_extension(language):
    """Returns the file extension for the given programming language."""
    return {"python": "py", "javascript": "js", "java": "java"}.get(language, "py")


def get_js_callgraph_cg(file_path):
    try:
        command_to_run = [
            "js-callgraph",
            "--cg",
            file_path,
            "--output",
            file_path.replace(".js", ".json"),
        ]

        # Run the command and capture the output and error
        result = subprocess.run(
            command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Check if the command was successful
        cg = {}
        if result.returncode == 0:
            print("Command Output:\n", result.stdout)
            # read the output file in ./out/callgraph.out and return contents
            with open(file_path.replace(".js", ".json"), "r") as file:
                # TODO: Translate the output to SWARM Format JSON
                cg_json = json.load(file)
                cg = convert_js_callgraph(cg_json)

        else:
            print("Command Failed with return code", result.returncode)
            print("Error Output:\n", result.stderr)

    except FileNotFoundError:
        print("Error: The specified file was not found.")
    except Exception as e:
        logger.error(f"Error running js_callgraph test: {e}")
        raise

    return json.dumps(cg, indent=4)


# Function to process the test folder
def process_test_folder(file_folder):
    try:
        file_path = os.path.join(file_folder, f"main.js")
        result_filepath = os.path.join(file_folder, f"main_result.json")

        output = get_js_callgraph_cg(file_path)

        with open(result_filepath, "w") as file:
            file.write(output)

    except Exception as e:
        logger.error(f"{file_path} failed: {e}")
        raise
