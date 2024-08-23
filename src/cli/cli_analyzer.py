import argparse


def parse_analyzer_args():
    """
    Parse command-line arguments for the results analyzer.
    """
    parser = argparse.ArgumentParser(
        description="Analyze benchmark evaluation results."
    )
    parser.add_argument(
        "--results_dir", help="Directory containing the results.", default=None
    )
    parser.add_argument(
        "--output_dir", help="Directory to save the analysis results.", default=None
    )
    parser.add_argument(
        "--analyze_metric",
        help="Metric to analyze (e.g., soundness, completeness).",
        choices=["soundness", "completeness", "accuracy", "sensitivity"],
        required=False,
    )
    return parser.parse_args()
