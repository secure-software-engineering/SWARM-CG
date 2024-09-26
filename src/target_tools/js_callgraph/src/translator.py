import copy
import json
import os
import re
import glob
import esprima
import utils
from collections import defaultdict

logger = utils.setup_logger()

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
        print(f"An error occurred generating AST: {e}")
        return None


def extract_class_method_hierarchy(ast):
    """
    Extracts class method hierarchy and object instantiations from the AST.

    Args:
    - ast (esprima.nodes.Script): The AST of the JavaScript code.

    Returns:
    - class_methods (dict): A dictionary mapping class names to their methods.
    - object_instantiations (dict): A dictionary mapping object names to their class names.
    """
    class_methods = defaultdict(list)
    object_instantiations = {}

    if ast:
        if ast.body:
            # Loop through the body of the AST
            for node in ast.body:
                # If it's a class declaration
                if isinstance(node, esprima.nodes.ClassDeclaration):
                    class_name = node.id.name
                    # Loop through the class body to find methods
                    for body_node in node.body.body:
                        if isinstance(body_node, esprima.nodes.MethodDefinition):
                            method_name = body_node.key.name
                            class_methods[class_name].append(method_name)

                # If it's a variable declaration
                elif isinstance(node, esprima.nodes.VariableDeclaration):
                    for declaration in node.declarations:
                        if declaration.init and isinstance(
                            declaration.init, esprima.nodes.NewExpression
                        ):
                            class_name = declaration.init.callee.name
                            object_name = declaration.id.name
                            object_instantiations[object_name] = class_name
    return class_methods, object_instantiations


def translate_js_callgraph_to_swarm(js_callgraph, class_methods, object_instantiations):
    swarm_json = defaultdict(list)

    for entry in js_callgraph:
        source_label = entry["source"]["label"]
        target_label = entry["target"]["label"]

        # Initialize full_source_label and full_target_label as None
        full_target_label = None
        full_source_label = None

        # Check class methods first
        for class_name, methods in class_methods.items():
            if target_label in methods:
                full_target_label = f"main.{class_name}.{target_label}"
                break

        for class_name, methods in class_methods.items():
            if source_label in methods:
                full_source_label = f"main.{class_name}.{source_label}"
                break

        # If the method wasn't found in the class context, check for object instantiation
        if not full_target_label and target_label in object_instantiations:
            class_name = object_instantiations[target_label]
            full_target_label = f"main.{class_name}.{target_label}"

        if not full_source_label and source_label in object_instantiations:
            class_name = object_instantiations[source_label]
            full_source_label = f"main.{class_name}.{source_label}"

        # If still not found, fall back to built-in functions or default target
        if not full_target_label:
            translated_builtin = translate_builtin_function(target_label)
            if translated_builtin:
                full_target_label = translated_builtin
            else:
                full_target_label = f"main.{target_label}"

        # If still not found, fall back to built-in functions or default source
        if not full_source_label:
            translated_builtin = translate_builtin_function(source_label)
            if translated_builtin:
                full_source_label = translated_builtin
            else:
                full_source_label = f"main.{source_label}"

        if source_label == "global":
            full_source_label = "main"
        swarm_json[full_source_label].append(full_target_label)

    return swarm_json


def convert_js_callgraph(js_file_path, js_callgraph):

    try:
        # Attempt to generate the AST
        ast = generate_ast_from_js_file(js_file_path)

        # If AST generation fails, use empty class_methods and object_instantiations
        if ast is None:
            print(
                f"AST is None for {js_file_path}. Continuing with default translation."
            )
            logger.info(f"AST is None for:  {js_file_path}")
            class_methods, object_instantiations = defaultdict(list), {}
        else:
            # Extract class method hierarchy and object instantiations from AST
            class_methods, object_instantiations = extract_class_method_hierarchy(ast)

            # Log class methods and object instantiations
            logger.info(f"AST Generated for file path:\n{js_file_path}")
            logger.info(f"Class Methods:\n{json.dumps(class_methods, indent=2)}")
            logger.info(
                f"Object Instantiations:\n{json.dumps(object_instantiations, indent=2)}"
            )
            # logger.debug(f"AST (raw): {ast}")

    except Exception as e:
        # Catch any exceptions and proceed with empty class methods and object instantiations
        print(f"An error occurred while processing {js_file_path}: {e}")
        logger.error(f"An error occurred while generating AST for {js_file_path}: {e}")
        class_methods, object_instantiations = defaultdict(list), {}

    # Translate the call graph to swarm.json format
    swarm_json = translate_js_callgraph_to_swarm(
        js_callgraph, class_methods, object_instantiations
    )
    return swarm_json
