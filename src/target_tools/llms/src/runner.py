import argparse
import json
import logging
import multiprocessing
import os
import re
import shutil
import sys
import time
import traceback
from pathlib import Path
from sys import stdout
from typing import List, Optional

import prompts
import translator
import utils
import vllm_helpers
import transformers_helpers
import openai_helpers

from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest
import gc
import torch
from tqdm import tqdm


AUTOFIX_WITH_OPENAI = False
REQUEST_TIMEOUT = 60
USE_MULTIPROCESSING_FOR_TERMINATION = True
MAX_TOKENS = 64
TEMPARATURE = 0.001
MAX_NEW_TOKENS = 1024

script_dir = Path(__file__).parent
# Create a logger
logger = logging.getLogger("runner")
logger.setLevel(logging.DEBUG)

if utils.is_running_in_docker():
    file_handler = logging.FileHandler("/tmp/llm_log.log", mode="w")
else:
    file_handler = logging.FileHandler("llm_log.log", mode="w")

file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_prompt_mapping(
    prompt_template, python_files, use_system_prompt=False, language=None
):
    id_mapping = {
        idx: {
            "file_path": file_path,
            "json_filepath": os.path.join(file_path, "callgraph.json"),
            "result_filepath": os.path.join(file_path, f"main_result.json"),
            "result_dump_filepath": os.path.join(file_path, f"response_dump.txt"),
            "prompt": utils.get_prompt(
                prompt_template,
                file_path,
                use_system_prompt=use_system_prompt,
                language=language,
            ),
        }
        for idx, file_path in enumerate(python_files)
    }

    return id_mapping


def create_result_json_file(file_info, output_raw, prompt_template):
    output = re.sub(r"```json", "", output_raw)
    output = re.sub(r"```", "", output)
    output = re.sub(r"<\|assistant\|>\\n", "", output)

    with open(file_info["result_dump_filepath"], "w") as f:
        f.write(output_raw)

    # TODO: Improve the way this is done. Some plugin based design.
    if prompt_template in [
        "prompt_template_questions_based_1_py",
        "prompt_template_questions_based_1_js",
    ]:
        answers_json = utils.generate_json_from_answers(
            file_info["json_filepath"], output
        )

        # translated_json = translator.translate_content(answers_json)
    # else:
    #     translated_json = translator.translate_content(output)

    is_valid_json = utils.generate_json_file(file_info["result_filepath"], answers_json)
    if not is_valid_json:
        logger.info(f"{file_info['file_path']} failed: Not a valid JSON")
        # raise utils.JsonException("json")

    # logger.info(f"Processed file: {file_info['file_path']}")


def list_files(benchmark_folder_path):
    files = []
    for cat in sorted(os.listdir(benchmark_folder_path)):
        files_analyzed = 0
        tests = os.listdir(os.path.join(benchmark_folder_path, cat))

        # Iterating through each test in a category
        for test in tests:
            file = os.path.join(benchmark_folder_path, cat, test)
            files.append(file)

    return files


def model_evaluation_vllm(
    model_name,
    prompt_template,
    python_files,
    engine,
    results_dst,
    use_system_prompt=False,
    lora_request=None,
    sampling_params=None,
    language=None,
):

    id_mapping = get_prompt_mapping(
        prompt_template, python_files, use_system_prompt, language
    )

    prompts = [x["prompt"] for x in id_mapping.values()]

    processed_prompts = engine.tokenizer.tokenizer.apply_chat_template(
        prompts, tokenize=False, add_generation_template=True
    )

    request_outputs = vllm_helpers.process_requests(
        engine, processed_prompts, sampling_params, lora_request
    )

    for r_output in request_outputs:
        file_info = id_mapping[int(r_output.request_id)]

        output_raw = r_output.outputs[0].text
        create_result_json_file(file_info, output_raw, prompt_template)


def model_evaluation_transformers(
    model_name,
    prompt_template,
    python_files,
    pipe,
    results_dst,
    use_system_prompt=False,
    batch_size=32,
    language=None,
):

    id_mapping = get_prompt_mapping(
        prompt_template, python_files, use_system_prompt, language
    )

    prompts = [x["prompt"] for x in id_mapping.values()]

    # processed_prompts = pipe.tokenizer.apply_chat_template(
    #     prompts, tokenize=False, add_generation_template=True
    # )

    # Split prompts into batches
    progress_batch = batch_size
    for i in tqdm(range(0, len(prompts), progress_batch)):
        prompt_batch = prompts[i : i + progress_batch]

        request_outputs = transformers_helpers.process_requests(
            pipe,
            prompt_batch,
            max_new_tokens=MAX_NEW_TOKENS,
            batch_size=batch_size,
        )

        for id, r_output in enumerate(request_outputs):
            file_info = id_mapping[id + i]

            output_raw = r_output[0]["generated_text"][-1]["content"]

            # output_raw = r_output[0]["generated_text"].split(pipe.tokenizer.eos_token)[-1]
            # output_raw = r_output[0]["generated_text"].split("[/INST]")[-1]

            create_result_json_file(file_info, output_raw, prompt_template)


def model_evaluation_openai(
    model_name,
    prompt_template,
    openai_key,
    python_files,
    results_dst,
    use_system_prompt=False,
    language=None,
):

    id_mapping = get_prompt_mapping(
        prompt_template, python_files, use_system_prompt, language
    )

    prompts = [x["prompt"] for x in id_mapping.values()]

    utils.dump_ft_jsonl(id_mapping, f"{results_dst}/ft_dataset.jsonl")
    utils.dump_batch_prompt_jsonl(id_mapping, f"{results_dst}/batch_prompt.jsonl")

    request_outputs = openai_helpers.process_requests(
        model_name,
        prompts,
        openai_key,
        max_new_tokens=MAX_NEW_TOKENS,
        max_workers=3,
    )

    for id, r_output in enumerate(request_outputs):
        file_info = id_mapping[id]

        output_raw = r_output
        create_result_json_file(file_info, output_raw, prompt_template)


def main_runner(args, runner_config, models_to_run, openai_models_models_to_run):
    runner_start_time = time.time()
    for model in models_to_run:
        error_count = 0
        timeout_count = 0
        json_count = 0
        files_analyzed = 0

        # Create result folder for model specific results
        benchmark_path = Path(args.benchmark_path)
        results_src = benchmark_path
        # TODO: Fix naming of the results folder
        if args.results_dir is None:
            results_dst = benchmark_path.parent / model["name"] / "benchmarks"
        else:
            results_dst = Path(args.results_dir) / model["name"] / "benchmarks"
            os.makedirs(results_dst, exist_ok=True)

        utils.copy_folder(results_src, results_dst)

        python_files = list_files(results_dst)

        pipe = None
        try:
            if model["use_vllms_for_evaluation"]:
                engine = vllm_helpers.initialize_engine(
                    model["model_path"],
                    model["quantization"],
                    model["lora_repo"],
                    model["max_model_len"],
                )
                lora_request = None
                if model["lora_repo"] is not None:
                    lora_request = LoRARequest(
                        f"{model['name']}-lora", 1, model["lora_repo"]
                    )

                sampling_params = SamplingParams(
                    temperature=TEMPARATURE, top_p=0.95, max_tokens=MAX_TOKENS
                )
                model_start_time = time.time()
                model_evaluation_vllm(
                    model["name"],
                    args.prompt_id,
                    python_files,
                    engine,
                    results_dst,
                    use_system_prompt=model["use_system_prompt"],
                    lora_request=lora_request,
                    sampling_params=sampling_params,
                    language=args.language,
                )

                del engine
                gc.collect()
                torch.cuda.empty_cache()
            else:
                if model["lora_repo"] is None:
                    model_path = model["model_path"]
                else:
                    model_path = model["lora_repo"]

                pipe = transformers_helpers.load_model_and_configurations(
                    args.hf_token, model_path, model["quantization"], TEMPARATURE
                )
                model_start_time = time.time()
                model_evaluation_transformers(
                    model["name"],
                    args.prompt_id,
                    python_files,
                    pipe,
                    results_dst,
                    use_system_prompt=model["use_system_prompt"],
                    batch_size=model["batch_size"],
                    language=args.language,
                )

                del pipe
                gc.collect()
                torch.cuda.empty_cache()

        except Exception as e:
            logger.error(f"Error in model {model['name']}: {e}")
            if pipe is not None:
                del pipe
            gc.collect()
            torch.cuda.empty_cache()

        logger.info(
            f"Model {model['name']} finished in {time.time()-model_start_time:.2f} seconds"
        )
        # logger.info("Running translator")
        # translator.main_translator(results_dst)

    # running gpt models
    for model in openai_models_models_to_run:
        error_count = 0
        timeout_count = 0
        json_count = 0
        files_analyzed = 0

        # Create result folder for model specific results
        benchmark_path = Path(args.benchmark_path)
        results_src = benchmark_path
        if args.results_dir is None:
            results_dst = benchmark_path.parent / model["name"] / benchmark_path.name
        else:
            results_dst = Path(args.results_dir) / model["name"] / benchmark_path.name
            os.makedirs(results_dst, exist_ok=True)

        utils.copy_folder(results_src, results_dst)

        python_files = list_files(results_dst)

        model_start_time = time.time()
        model_evaluation_openai(
            model["name"],
            args.prompt_id,
            args.openai_key,
            python_files,
            results_dst,
            use_system_prompt=model["use_system_prompt"],
            language=args.language,
        )

        logger.info(
            f"Model {model['name']} finished in {time.time()-model_start_time:.2f} seconds"
        )
        # logger.info("Running translator")
        # translator.main_translator(results_dst)

    logger.info(
        f"Runner finished in {time.time()-runner_start_time:.2f} seconds, with errors:"
        f" {error_count} | JSON errors: {json_count}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--language",
        choices=["python", "java", "javascript"],
        required=True,
        default="python",
        help="Language setting for the runner",
    )
    parser.add_argument(
        "--benchmark_path",
        help="Specify the benchmark path",
        default="/tmp/benchmarks",
    )

    parser.add_argument(
        "--results_dir",
        help="Specify the benchmark path",
        default=None,
    )

    parser.add_argument("--hf_token", help="Specify the hf token", required=True)

    parser.add_argument(
        "--openai_key", help="Specify the OpenAI Auth Key", required=False
    )

    parser.add_argument("--prompt_id", help="Specify the prompt ID", required=True)

    parser.add_argument(
        "--models_config",
        type=str,
        default=f"{script_dir}/models_config.yaml",
    )

    parser.add_argument(
        "--models",
        nargs="+",
        type=str,
        help="Space-separated list of models",
    )

    parser.add_argument(
        "--custom_models",
        nargs="+",
        type=str,
        help="Space-separated list of custom models",
    )

    parser.add_argument(
        "--openai_models",
        nargs="+",
        type=str,
        help="Space-separated list of openai models",
    )

    parser.add_argument(
        "--enable_streaming",
        help="If LLM response should be streamed",
        type=bool,
        default=False,
    )

    args = parser.parse_args()

    # Set HF token
    os.environ["HF_TOKEN"] = args.hf_token

    models_config = utils.load_models_config(parser.parse_args().models_config)
    runner_config = utils.load_runner_config(parser.parse_args().models_config)

    models_to_run = []
    openai_models_models_to_run = []
    # check if args.models are in models_config

    if args.models:
        for model in args.models:
            if model not in models_config["models"]:
                logger.error(f"Model {model} not found in models_config")
                sys.exit(-1)
            else:
                models_to_run.append(models_config["models"][model])

    # check if args.custom_models are in models_config
    if args.custom_models:
        for model in args.custom_models:
            if model not in models_config["custom_models"]:
                logger.error(f"Model {model} not found in models_config")
                sys.exit(-1)
            else:
                models_to_run.append(models_config["custom_models"][model])

    if args.openai_models:
        for model in args.openai_models:
            if model not in models_config["openai_models"]:
                logger.error(f"Model {model} not found in models_config")
                sys.exit(-1)
            else:
                openai_models_models_to_run.append(
                    models_config["openai_models"][model]
                )

    main_runner(args, runner_config, models_to_run, openai_models_models_to_run)

# example usage:
"""
python runner.py \
--benchmark_path /home/ssegpu/TypeEvalPy/TypeEvalPy/micro-benchmark \
--prompt_id prompt_template_questions_based_2 \
--models gemma2-it:2b codellama-it:7b codellama-it:13b codellama-it:34b llama3.1-it:8b llama3.1-it:70b tinyllama:1.1b phi3-small-it:7.3b phi3-medium-it:14b phi3-mini-it:3.8b phi3.5-mini-it:3.8b phi3.5-moe-it:41.9b mixtral-v0.1-it:8x7b mistral-v0.3-it:7b mistral-nemo-it-2407:12.2b mistral-large-it-2407:123b codestral-v0.1:22b \
--hf_token  \
--openai_key token \
--enable_streaming True \
--models_config /home/ssegpu/TypeEvalPy/TypeEvalPy/src/target_tools/llms/src/models_config.yaml \
--results_dir /home/ssegpu/TypeEvalPy/TypeEvalPy/.scrapy/results_final_1

python runner.py \
--benchmark_path /home/ssegpu/TypeEvalPy/TypeEvalPy/autogen_typeevalpy_benchmark \
--prompt_id prompt_template_questions_based_2 \
--models llama3.1-it:8b \
--hf_token  \
--openai_key token \
--enable_streaming True \
--models_config /home/ssegpu/TypeEvalPy/TypeEvalPy/src/target_tools/llms/src/models_config.yaml \
--results_dir /home/ssegpu/TypeEvalPy/TypeEvalPy/.scrapy/results_full_1
"""
