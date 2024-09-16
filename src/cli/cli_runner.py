import argparse


def parse_runner_args():
    """
    Parse command-line arguments for running micro-benchmarks against target tools.
    """
    parser = argparse.ArgumentParser(description="SWARM-CG: Run micro-benchmarks")
    parser.add_argument(
        "--language",
        choices=["python", "java", "javascript"],
        required=True,
        help="Specify the language of the micro-benchmarks.",
    )
    parser.add_argument(
        "--benchmark_name",
        required=True,
        help="Specify the name of the micro-benchmark (eg: pycg, swarm_js).",
    )
    parser.add_argument(
        "--tool",
        nargs="+",  # Allow multiple values
        choices=["ollama", "pycg", "llms", "headergen_cs"],  # Add more tools as needed
        help="Specify the target tool(s) for call graph construction.",
    )
    parser.add_argument(
        "--models",
        nargs="+",  # Allow multiple values
        default=["codellama:7b-python"],
        help="List of models to test with the specified tool.",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode with detailed logging."
    )
    parser.add_argument(
        "--nocache", action="store_true", help="Disable Docker image cache."
    )
    return parser.parse_args()
