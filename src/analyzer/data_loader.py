from pathlib import Path


def load_data(model_dir: Path):
    # Load and preprocess data from model_dir
    data = {}
    # Example: Load specific data files into the dictionary
    data["results"] = load_results_file(model_dir / "results.json")
    return data


def load_results_file(file_path):
    # Load the results file
    pass
