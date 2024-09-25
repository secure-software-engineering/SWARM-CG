import copy
import json
import os
import re
import glob
import esprima
from collections import defaultdict

built_in_mapping = {
    "Array_prototype_join": "<**JSArray**>.join",
    "String_prototype_split": "<**JSString**>.split",
    "Array_prototype_map": "<builtin>.Array.map",
    "Array_prototype_keys": "<builtin>.Array.keys",
}


def translate_builtin_function(label):
    if label in built_in_mapping:
        return built_in_mapping[label]
    return None


def generate_ast_from_js_file(file_path):
    """
    Generates the AST of the given JavaScript file using Esprima.

    Args:
    - file_path (str): The path to the JavaScript file.

    Returns:
    - ast (dict): The generated AST as a dictionary.
    """
    try:
        # Read the JavaScript code from the file
        with open(file_path, "r", encoding="utf-8") as js_file:
            js_code = js_file.read()

        # Parse the JavaScript code to generate AST
        ast = esprima.parseScript(js_code, {"tolerant": True, "loc": True})

        # Return the generated AST
        return ast
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_class_method_hierarchy(ast):
    """
    Extracts class method hierarchy and object instantiations from the AST.

    Args:
    - ast (dict): The AST of the JavaScript code.

    Returns:
    - class_methods (dict): A dictionary mapping class names to their methods.
    - object_instantiations (dict): A dictionary mapping object names to their class names.
    """
    class_methods = defaultdict(list)
    object_instantiations = {}

    # Recursively traverse the AST nodes
    def traverse(node, parent_class=None):
        if node is None:
            return

        if isinstance(node, dict):
            # If it's a class declaration
            if node.get("type") == "ClassDeclaration":
                class_name = node["id"]["name"]
                # Traverse class body to find methods
                for body_node in node["body"]["body"]:
                    if body_node["type"] == "MethodDefinition":
                        method_name = body_node["key"]["name"]
                        class_methods[class_name].append(method_name)
                # Traverse deeper into the class body
                traverse(node["body"], class_name)

            # If it's a variable declaration (object instantiation)
            if node.get("type") == "VariableDeclaration":
                for declaration in node["declarations"]:
                    if (
                        declaration["init"]
                        and declaration["init"].get("type") == "NewExpression"
                    ):
                        class_name = declaration["init"]["callee"]["name"]
                        object_name = declaration["id"]["name"]
                        object_instantiations[object_name] = class_name

            # Traverse all the child nodes recursively
            for key, value in node.items():
                traverse(value, parent_class)

        elif isinstance(node, list):
            for item in node:
                traverse(item, parent_class)

    traverse(ast)
    return class_methods, object_instantiations


def translate_js_callgraph_to_swarm(js_callgraph, class_methods, object_instantiations):
    """
    Translates js_callgraph.json to the required swarm.json format.

    Args:
    - js_callgraph (list): The parsed JSON call graph from js-callgraph tool.
    - class_methods (dict): Mapping of class names to their methods.
    - object_instantiations (dict): Mapping of object names to class names.

    Returns:
    - swarm_json (dict): The translated call graph in swarm format.
    """
    swarm_json = defaultdict(list)

    for entry in js_callgraph:
        source_label = entry["source"]["label"]
        target_label = entry["target"]["label"]

        # Handle the 'global' source label (translated to 'main')
        if source_label == "global":
            source_label = "main"

        # Handle method calls like 'func', mapping to class.method
        # First check if the method belongs to a class using the class_methods dict
        full_target_label = None
        for class_name, methods in class_methods.items():
            if target_label in methods:
                full_target_label = f"main.{class_name}.{target_label}"
                break

        # If method belongs to an object instance, map it to the class
        if not full_target_label and target_label in object_instantiations:
            class_name = object_instantiations[target_label]
            full_target_label = f"main.{class_name}.{target_label}"

        # Default to using target_label if no class method or object found
        if not full_target_label:
            translated_builtin = translate_builtin_function(target_label)
            if translated_builtin:
                full_target_label = translated_builtin
            else:
                full_target_label = f"main.{target_label}"

        # Add the call graph entry to swarm format
        swarm_json[source_label].append(full_target_label)
        if full_target_label not in swarm_json:
            swarm_json[full_target_label] = []

    return swarm_json


def convert_js_callgraph(js_file_path, js_callgraph):

    # Step 1: Generate AST from the JavaScript file
    ast = generate_ast_from_js_file(js_file_path)

    if ast is None:
        print("Error generating AST.")
        return

    # Step 2: Extract class method hierarchy and object instantiations from AST
    class_methods, object_instantiations = extract_class_method_hierarchy(ast)

    # Step 4: Translate to swarm.json format
    swarm_json = translate_js_callgraph_to_swarm(
        js_callgraph, class_methods, object_instantiations
    )
    return swarm_json
