import utils
import json
import os
import re
import time 
import requests
import multiprocessing
from langchain.prompts import PromptTemplate
from langchain.output_parsers import OutputFixingParser

def is_ollama_online(server_url):
    try:
        res = requests.get(server_url)
        # Check if the request was successful
        if res.status_code == 200:
            # Check the content of the response
            if res.text == "Ollama is running":
                return True
        return False
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        print(f"An error occurred: {e}")
        return False

# Function to invoke LLM
def invoke_llm(llm, prompt, queue):
    try:
        output = llm.invoke(prompt)
        queue.put(output)
    except Exception as e:
        queue.put(e)

# Function to generate prompt
def get_prompt(prompt_id, code, json_filepath, answers_placeholders=True, test_folder=None, logger=None, language=None):
    # with open(json_filepath, "r") as file:
    #     data = json.load(file)
    
    if prompt_id in [
        "questions_based_1",
    ]:
        questions_from_json = utils.generate_questions_from_json(json_filepath)
        prompt_template = eval(f"prompts.{prompt_id}")

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["code", "questions", "answers", "language"],
        )

        prompt_data = {
            "code": code,
            "questions": "\n".join(questions_from_json),
            "answers": (
                "\n".join([f"{x}." for x in range(1, len(questions_from_json) + 1)])
                if answers_placeholders
                else ""
            ),
            "language": language.capitalize(),
        }
        # Save prompt_data to a JSON file for testing purposes
        if test_folder is not None:
            # Get test name from the file_path
            test_name = os.path.basename(test_folder)
            prompt_data_file = os.path.join(test_folder, f"{test_name}_promptdata.json")
            with open(prompt_data_file, "w") as file:
                json.dump(prompt_data, file, indent=2)
    else:
        if logger:
            logger.error("ERROR! Prompt not found!")
        raise ValueError("Prompt not found!")

    _input = prompt.format_prompt(**prompt_data)

    return _input.to_string()

# Returns language extension
def get_language_extension(language):
    """Returns the file extension for the given programming language."""
    return {
        "python": "py",
        "javascript": "js",
        "java": "java"
    }.get(language, "py")

# Function to gather code files from each test folder
def gather_code_files_from_test_folder(test_folder, language_extension):
    """Recursively gathers all code files with the specified language extension."""
    code_files = []
    for root, _, files in os.walk(test_folder):
        for file in files:
            if file.endswith(f".{language_extension}"):
                code_files.append(os.path.join(root, file))
    return code_files

# Function to process the test folder
def process_test_folder(file_path, llm, openai_llm, prompt_id, language, logger=None, request_timeout=60, autofix_with_openai=False, use_multiprocessing_for_termination=True, parser=None):
    file_start_time = time.time()
    try:
        json_filepath = os.path.join(file_path, "callgraph.json")
        result_filepath = os.path.join(file_path, f"main_result.json")
        result_dump_filepath = os.path.join(file_path, f"response_dump.txt")

        # Use language_extension function to get the correct language file extension
        extension = get_language_extension(language)

        # Gather all relevant code files
        code_files = gather_code_files_from_test_folder(file_path, extension)

        # Concatenate code contents
        code = ""
        for code_file in code_files:
            with open(code_file, "r") as file:
                code_content = file.read()
                # Add filename to the code content for context
                code += f"\n# File: {os.path.basename(code_file)}\n{code_content}\n"

        # Remove comments from code but keep line number structure
        code = "\n".join(
            [line if not line.startswith("#") else "#" for line in code.split("\n")]
        )

        if use_multiprocessing_for_termination:
            # Queue for communication between processes
            queue = multiprocessing.Queue()

            # Create a process for llm.invoke
            process = multiprocessing.Process(
                target=invoke_llm,
                args=(llm, get_prompt(prompt_id, code, json_filepath, test_folder=file_path, logger=logger, language=language), queue),
            )
            process.start()

            # Wait for the process to finish with a timeout (e.g., 60 seconds)
            process.join(timeout=request_timeout)

            if process.is_alive():
                if logger:
                    logger.info(f"Timeout occurred for {file_path}")
                process.terminate()  # Terminate the process if it's still running
                process.join()
                if logger:
                    logger.info(f"{file_path} failed: Not a valid JSON")
                raise utils.TimeoutException("json")

            result = queue.get_nowait()

            if isinstance(result, Exception):
                raise result

            output = result
        else:
            output = llm.invoke(get_prompt(prompt_id, code, json_filepath, test_folder=file_path, logger=logger, language=language))

        # if isinstance(llm, ChatOpenAI):
        #     output = output.content

        with open(result_dump_filepath, "w") as file:
            file.write(output)

        # TODO: Include this in langchain pipeline
        output = re.sub(r"```json", "", output)
        output = re.sub(r"```", "", output)

        if autofix_with_openai and parser:
            new_parser = OutputFixingParser.from_llm(parser=parser, llm=openai_llm)
            output = new_parser.parse(output)

        if logger:
            logger.info(
                "File processed for model"
                f" {llm.model if getattr(llm, 'model', False) else llm.model_name} finished"
                f" in: {time.time()-file_start_time:.2f}"
            )

    except Exception as e:
        if logger:
            logger.error(f"{file_path} failed: {e}")
        raise

    if logger:
        logger.info(output)

    # TODO: Improve the way this is done. Some plugin based design.
    if prompt_id in ["questions_based_1"]:
        translated_json = utils.generate_json_from_answers(json_filepath, output)
    else:
        translated_json = output

    is_valid_json = utils.generate_json_file(result_filepath, translated_json)
    if not is_valid_json:
        if logger:
            logger.info(f"{file_path} failed: Not a valid JSON")
        raise utils.JsonException("json")