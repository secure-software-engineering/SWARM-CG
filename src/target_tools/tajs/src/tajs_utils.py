import utils
import json
import os
import subprocess
from translator import convert_tajs

logger = utils.setup_logger()


# Returns language extension
def get_language_extension(language):
    """Returns the file extension for the given programming language."""
    return {"python": "py", "javascript": "js", "java": "java"}.get(language, "py")


def get_tajs_cg(file_path, path_to_jar):
    try:
        command_to_run = [
            "java",
            "-jar",
            path_to_jar,
            "-callgraph",
            "-quiet",
            file_path,
        ]
        try:
            os.rmdir(f"{os.getcwd()}/out")
        except OSError:
            pass

        # Run the command and capture the output and error
        result = subprocess.run(
            command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Check if the command was successful
        cg = {}
        if result.returncode == 0:
            print("Command Output:\n", result.stdout)
            # read the output file in ./out/callgraph.out and return contents
            with open(f"{os.getcwd()}/out/callgraph.dot", "r") as file:
                # TODO: Translate the output to SWARM Format JSON
                convert_tajs(f"{os.getcwd()}/out")
                with open(f"{os.getcwd()}/out/output_callgraph.json", "r") as f:
                    cg = json.load(f)

            # delete the output dir not exist ok

        else:
            print("Command Failed with return code", result.returncode)
            print("Error Output:\n", result.stderr)

    except FileNotFoundError:
        print("Error: Java or the specified file was not found.")
    except Exception as e:
        logger.error(f"Error running TAJS test: {e}")
        raise

    try:
        os.rmdir(f"{os.getcwd()}/out")
    except OSError:
        pass
    return json.dumps(cg, indent=4)


# Function to process the test folder
def process_test_folder(file_folder, path_to_jar="/usr/src/app/dist/tajs-all.jar"):
    try:
        file_path = os.path.join(file_folder, f"main.js")
        result_filepath = os.path.join(file_folder, f"main_result.json")

        output = get_tajs_cg(file_path, path_to_jar)

        with open(result_filepath, "w") as file:
            file.write(output)

    except Exception as e:
        logger.error(f"{file_path} failed: {e}")
        raise
