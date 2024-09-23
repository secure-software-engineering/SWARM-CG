import copy
import json
import os
import re
import glob


def convert_js_callgraph(cg_json):
    """
    Translates the js-callgraph output JSON to Swarm's JSON format.

    :param cg_json: js-callgraph JSON
    """
    try:
        # Initialize the call graph for Swarm format
        swarm_callgraph = {}

        def get_swarm_function_name(label):
            if label == "global":
                return "main"
            return f"main.{label}"

        # Translate the js-callgraph format to Swarm's format
        for entry in cg_json:
            # Extract the source and target function labels
            source_label = entry["source"]["label"]
            target_label = entry["target"]["label"]

            swarm_source = get_swarm_function_name(source_label)
            swarm_target = get_swarm_function_name(target_label)

            # Ensure the source function exists in the swarm_callgraph dictionary
            if swarm_source not in swarm_callgraph:
                swarm_callgraph[swarm_source] = []

            # Add the target function to the source function's list if it's not already present
            if swarm_target not in swarm_callgraph[swarm_source]:
                swarm_callgraph[swarm_source].append(swarm_target)

            # Ensure the target function exists in the swarm_callgraph dictionary, even if it has no callees
            if swarm_target not in swarm_callgraph:
                swarm_callgraph[swarm_target] = []

            print(f"Successfully translated {cg_json} to {swarm_callgraph}")
    except Exception as e:
        print(f"Error translating {cg_json}: {str(e)}")
    return swarm_callgraph
