import os
import json


def convert_callgraph(callgraph):
    """
    Convert callgraph format from the original format to the target format.
    """
    converted = {}
    for item in callgraph:
        caller = item.get("caller")
        callees = [target.get("callee") for target in item.get("targets", [])]
        converted[caller] = callees
    return converted


def process_json_files(root_path):
    """
    Traverse the directory structure starting from root_path, convert each callgraph.json file,
    and overwrite it with the converted format.
    """
    for dirpath, _, filenames in os.walk(root_path):
        if "callgraph.json" in filenames:
            file_path = os.path.join(dirpath, "callgraph.json")

            # Read the JSON file
            with open(file_path, "r") as file:
                try:
                    callgraph = json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Error reading {file_path}: {e}")
                    continue

            # Convert the callgraph
            converted_callgraph = convert_callgraph(callgraph)

            # Overwrite the original callgraph.json file with the converted callgraph
            with open(file_path, "w") as file:
                json.dump(converted_callgraph, file, indent=4)

            print(f"Converted and overwritten {file_path}")


# Specify the root path to the 'cats' folder
root_path = "../../benchmarks/java/cats"
process_json_files(root_path)
