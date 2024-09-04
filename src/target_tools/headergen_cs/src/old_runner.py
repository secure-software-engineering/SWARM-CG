import argparse
import json
import logging
from pathlib import Path
from sys import stdout

import translator
import utils
from headergen import headergen

# Create a logger
logger = logging.getLogger("runner")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("/tmp/<tool_name>_log.log")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def list_python_files(folder_path):
    python_files = sorted(Path(folder_path).rglob("*.py"))
    return python_files


def process_file(file_path):
    analysis_meta = headergen.get_analysis_output(file_path, "/tmp")
    return analysis_meta


def main_runner(args):
    python_files = list_python_files(args.bechmark_path)
    files_analyzed = 0
    error_count = 0
    for file in python_files:
        try:
            logger.info(file)

            # TODO: Run the inference here and gather results in /tmp/results
            inferred = process_file(file)

            # TODO: Save translated file to the same folder /tmp/results
            json_file_path = str(file).replace(".py", "_result.json")

            with open(json_file_path, "w") as json_file:
                inferred_serializable = inferred["types_formatted"]
                json.dump(inferred_serializable, json_file, sort_keys=True, indent=4)

        except Exception as e:
            logger.info(f"Command returned non-zero exit status: {e} for file: {file}")
            error_count += 1

        files_analyzed += 1
        logger.info(f"Progress: {files_analyzed}/{len(python_files)}")

    logger.info(f"Runner finished with errors:{error_count}")


if __name__ == "__main__":
    is_running_in_docker = utils.is_running_in_docker()
    if is_running_in_docker:
        print("Python is running inside a Docker container")
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--bechmark_path",
            help="Specify the benchmark path",
            default="/tmp/micro-benchmark",
        )

        args = parser.parse_args()
        main_runner(args)
    else:
        print("Python is not running inside a Docker container")
        file_path = ""
        process_file(file_path)
