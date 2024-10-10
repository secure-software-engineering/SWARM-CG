from pathlib import Path
import os
import utils
import json
from runner import create_result_json_file, get_prompt_mapping


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


models = [
    # {
    #     "name": "gpt-4o_hg_cs",
    #     "path": "/mnt/Projects/PhD/Research/TypeEvalPy/git_sources/TypeEvalPy_test/.scrapy/batch_prompts_results/gpt-4o_hg_cs-batch_1PSl4bmOdffJdyRraiOPbleP.jsonl",
    #     "bechmark_path": Path(
    #         "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/benchmarks/python/headergen"
    #     ),
    #     "prompt_template": "prompt_template_questions_based_1_py_callsites",
    # },
    # {
    #     "name": "gpt-4o-mini_hg_cs",
    #     "path": "/mnt/Projects/PhD/Research/TypeEvalPy/git_sources/TypeEvalPy_test/.scrapy/batch_prompts_results/gpt-4o-mini_hg_cs-batch_3dK2KOYlkhovzS7Qmqbs0Cnc.jsonl",
    #     "bechmark_path": Path(
    #         "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/benchmarks/python/headergen"
    #     ),
    #     "prompt_template": "prompt_template_questions_based_1_py_callsites",
    # },
    {
        "name": "gpt-4o_js",
        "path": "/mnt/Projects/PhD/Research/TypeEvalPy/git_sources/TypeEvalPy_test/.scrapy/batch_prompts_results/gpt-4o_js-batch_YE7JzcBsKLSeZ7CeoeGIkCdZ.jsonl",
        "bechmark_path": Path(
            "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/benchmarks/javascript/pycg_js"
        ),
        "prompt_template": "prompt_template_questions_based_1_js",
    },
    {
        "name": "gpt-4o_pycg",
        "path": "/mnt/Projects/PhD/Research/TypeEvalPy/git_sources/TypeEvalPy_test/.scrapy/batch_prompts_results/gpt-4o_pycg-batch_uGBHKpb5oeIHVaBNXUQCdipr.jsonl",
        "bechmark_path": Path(
            "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/benchmarks/python/pycg"
        ),
        "prompt_template": "prompt_template_questions_based_1_py",
    },
    {
        "name": "gpt-4o-mini_js",
        "path": "/mnt/Projects/PhD/Research/TypeEvalPy/git_sources/TypeEvalPy_test/.scrapy/batch_prompts_results/gpt-4o-mini_js-batch_rbNCMtcZIUyzD9aZ4QQ2RsIu.jsonl",
        "bechmark_path": Path(
            "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/benchmarks/javascript/pycg_js"
        ),
        "prompt_template": "prompt_template_questions_based_1_js",
    },
    {
        "name": "gpt-4o-mini_pycg",
        "path": "/mnt/Projects/PhD/Research/TypeEvalPy/git_sources/TypeEvalPy_test/.scrapy/batch_prompts_results/gpt-4o-mini_pycg-batch_Nk9np2B9rhzD3AaDgMZEU7oB.jsonl",
        "bechmark_path": Path(
            "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/benchmarks/python/pycg"
        ),
        "prompt_template": "prompt_template_questions_based_1_py",
    },
]


results_dir = Path(
    "/mnt/Projects/PhD/Research/Student-Thesis/8_Rose/git_sources/SWARM-CG/.scrapy/batch_results_js_pycg"
)

for model in models:
    results_dst = Path(results_dir) / model["name"] / "benchmarks"
    os.makedirs(results_dst, exist_ok=True)

    utils.copy_folder(model["bechmark_path"], results_dst)

    python_files = list_files(results_dst)

    id_mapping = get_prompt_mapping(
        model["prompt_template"],
        python_files,
        use_system_prompt=True,
        language="javascript" if "js" in model["name"] else "python",
    )

    # read jsonl file and iterate over each line as json object
    with open(model["path"], "r") as f:
        for line in f:
            fact_json = json.loads(line)
            output_raw = fact_json["response"]["body"]["choices"][0]["message"][
                "content"
            ]
            r_id = int(fact_json["custom_id"].split("-")[-1])
            file_info = id_mapping[r_id]
            print(id_mapping[r_id]["file_path"])
            print(fact_json["custom_id"])

            create_result_json_file(file_info, output_raw, model["prompt_template"])
