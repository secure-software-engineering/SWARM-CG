import logging
from pathlib import Path
import re
import json
import os
import subprocess
import traceback

logger = logging.getLogger("sootup_runner")


def sanitize_method_signature(signature):
    """
    Sanitizes a method signature by preserving the method name and its parameters.
    Example: 'void main(java.lang.String[])' -> 'main(java.lang.String[])'
    """
    # Match method signature format (including parameters)
    method_pattern = re.compile(r"([^\s]+)\s+([^\(]+)\((.*)\)")
    match = method_pattern.match(signature)
    if match:
        # Return method with parameters
        return f"{match.group(2)}({match.group(3)})"
    else:
        # In case no parameters are found, return method with empty parentheses
        return f"{signature}()"


def parse_cg_to_swarm_json(txt_file_path, output_json_path):
    """
    :param txt_file_path: Path to .txt call graph file.
    :param output_json_path: Path to save the output JSON file.
    """
    call_graph = {}
    pattern = r'^\s*"<([^:]+):\s*([^\"]+)>"\s*->\s*"<([^:]+):\s*([^\"]+)>";\s*$'

    with open(txt_file_path, "r") as txt_file:
        for line in txt_file:

            stripped_line = line.strip()
            print(f"Pattern: {repr(pattern)}")
            print(f"Stripped line: {repr(stripped_line)}")
            match = re.match(pattern, stripped_line)
            print(stripped_line)
            if match:
                caller_class = match.group(1)
                caller_method = match.group(2)
                target_class = match.group(3)
                target_method = match.group(4)

                caller_method_sanitized = sanitize_method_signature(caller_method)
                target_method_sanitized = sanitize_method_signature(target_method)
                # Format caller and target to match the ground truth
                caller = f"{caller_class}:{caller_method_sanitized}"
                target = f"{target_class}:{target_method_sanitized}"

                # Append the target to the caller's list in the dictionary
                if caller not in call_graph:
                    call_graph[caller] = []
                call_graph[caller].append(target)

    # Save the call graph dictionary as JSON
    with open(output_json_path, "w") as json_file:
        json.dump(call_graph, json_file, indent=4)
    print(f"Call graph converted to JSON and saved to {output_json_path}")


def get_sootup_cg(test_file_path, jar_path, analysis_type="CHA"):
    """
    :param input_path: Path to testcase JAR file.
    :param jar_path: Path to the SootUp JAR.
    :param analysis_type: Analysis type (e.g., "CHA","RTA", etc).
    :return: Path to the output cg .txt file.
    """

    output_dir = Path(test_file_path).parent
    try:
        # Execute SootUp
        subprocess.run(
            ["java", "-jar", jar_path, str(test_file_path), analysis_type], check=True
        )
        print("JAR executed successfully.")

        # Find .txt file
        txt_files = list(output_dir.glob("*.txt"))

        if not txt_files:
            raise FileNotFoundError(
                f"No call graph .txt file generated in {output_dir}"
            )

        if len(txt_files) > 1:
            raise RuntimeError(
                f"Multiple .txt files found in {output_dir}, cannot determine call graph file"
            )
        # Return.txt file
        return txt_files[0]

    except subprocess.CalledProcessError as e:
        print(f"Error executing JAR: {e}")
        logger.error(f"Error executing SootUp on {test_file_path}: {e}")
        logger.debug(traceback.format_exc())
        raise
    except FileNotFoundError as fnf_error:
        logger.error(str(fnf_error))
        raise


def process_test_folder(file_folder, path_to_jar="lib", analysis_type="CHA"):
    """
    :param file_folder: Path to test folder.
    :param path_to_jar: Path to SootUp JAR files.
    """
    # Find .jar file
    jar_files = list(Path(file_folder).glob("*.jar"))
    if not jar_files:
        logger.error(f"No JAR file found in {file_folder}")
        return

    test_file_path = jar_files[0]
    sootup_jar_path = os.path.join(
        path_to_jar, "sootupcg-1.0-SNAPSHOT-jar-with-dependencies.jar"
    )
    try:
        # Run SootUp
        cg_txt_file = get_sootup_cg(test_file_path, sootup_jar_path, analysis_type)

        # output JSON path
        result_filepath = Path(file_folder) / "main_result.json"

        # Convert sootup .txt to swarm_js JSON format
        parse_cg_to_swarm_json(cg_txt_file, result_filepath)

        print(f"Call graph JSON created at {result_filepath}")

    except Exception as e:
        logger.error(f"Error processing {test_file_path}: {e}")
        logger.debug(traceback.format_exc())
        # Write an empty JSON object to the result file if processing fails
        result_filepath = Path(file_folder) / "main_result.json"
        with open(result_filepath, "w") as file:
            file.write(json.dumps({}))
