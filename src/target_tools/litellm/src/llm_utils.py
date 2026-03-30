import utils
import json
import os
import re
import time
import multiprocessing
import prompts
import litellm


def invoke_llm(model, prompt, api_base, temperature, timeout, queue):
    try:
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "timeout": timeout,
        }
        if api_base:
            kwargs["api_base"] = api_base
        response = litellm.completion(**kwargs)
        output = response.choices[0].message.content
        queue.put(output)
    except Exception as e:
        queue.put(e)


def get_prompt(
    prompt_id,
    code,
    json_filepath,
    answers_placeholders=True,
    test_folder=None,
    logger=None,
    language=None,
):
    if prompt_id in [
        "questions_based_1",
        "questions_based_1_py",
        "questions_based_1_js",
        "questions_based_1_java",
        "questions_based_1_py_callsites",
    ]:
        questions_from_json = utils.generate_questions_from_json(
            json_filepath, test_folder, logger
        )
        prompt_template = eval(f"prompts.{prompt_id}")

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

        formatted_prompt = prompt_template.format(**prompt_data)

        if test_folder is not None:
            prompt_file = os.path.join(test_folder, "prompt.txt")
            with open(prompt_file, "w") as file:
                file.write(formatted_prompt)
    else:
        if logger:
            logger.error("ERROR! Prompt not found!")
        raise ValueError("Prompt not found!")

    return formatted_prompt


def get_language_extension(language):
    """
    Returns the file extension for the given programming language.
    """
    return {"python": "py", "javascript": "js", "java": "java"}.get(language, "py")


def gather_code_files_from_test_folder(test_folder, language_extension):
    """Recursively gathers all code files with the specified language extension."""
    code_files = []
    for root, _, files in os.walk(test_folder):
        for file in files:
            if file.endswith(f".{language_extension}"):
                code_files.append(os.path.join(root, file))
    return code_files


def process_test_folder(
    file_path,
    model,
    api_base,
    prompt_id,
    language,
    logger=None,
    request_timeout=60,
    temperature=0.1,
    use_multiprocessing_for_termination=True,
):
    file_start_time = time.time()
    try:
        json_filepath = os.path.join(file_path, "callgraph.json")
        result_filepath = os.path.join(file_path, "main_result.json")
        result_dump_filepath = os.path.join(file_path, "response_dump.txt")

        extension = get_language_extension(language)
        code_files = gather_code_files_from_test_folder(file_path, extension)

        code = ""
        for code_file in code_files:
            with open(code_file, "r") as file:
                code_content = file.read()
                code += f"'''{os.path.basename(code_file)}\n{code_content}'''\n"

        # Remove comments from code but keep line number structure
        code = "\n".join(
            [line if not line.startswith("#") else "#" for line in code.split("\n")]
        )

        prompt = get_prompt(
            prompt_id,
            code,
            json_filepath,
            test_folder=file_path,
            logger=logger,
            language=language,
        )

        if use_multiprocessing_for_termination:
            queue = multiprocessing.Queue()

            process = multiprocessing.Process(
                target=invoke_llm,
                args=(model, prompt, api_base, temperature, request_timeout, queue),
            )
            process.start()
            process.join(timeout=request_timeout)

            if process.is_alive():
                if logger:
                    logger.info(f"Timeout occurred for {file_path}")
                process.terminate()
                process.join()
                if logger:
                    logger.info(f"{file_path} failed: Timeout")
                raise utils.TimeoutException("timeout")

            result = queue.get_nowait()

            if isinstance(result, Exception):
                raise result

            output = result
        else:
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "timeout": request_timeout,
            }
            if api_base:
                kwargs["api_base"] = api_base
            response = litellm.completion(**kwargs)
            output = response.choices[0].message.content

        with open(result_dump_filepath, "w") as file:
            file.write(output)

        output = re.sub(r"```json", "", output)
        output = re.sub(r"```", "", output)

        if logger:
            logger.info(
                f"File processed for model {model} finished"
                f" in: {time.time()-file_start_time:.2f}"
            )

    except Exception as e:
        if logger:
            logger.error(f"{file_path} failed: {e}")
        raise

    if logger:
        logger.info(output)

    if prompt_id.startswith("questions_based"):
        translated_json = utils.generate_json_from_answers(json_filepath, output)
    else:
        translated_json = output

    is_valid_json = utils.generate_json_file(result_filepath, translated_json)
    if not is_valid_json:
        if logger:
            logger.info(f"{file_path} failed: Not a valid JSON")
        raise utils.JsonException("json")
