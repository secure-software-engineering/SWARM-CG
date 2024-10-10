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
        "--analysis_output_dir",
        help="Directory to save the analysis results.",
        default=None,
    )
    parser.add_argument(
        "--analysis_metric",
        help="Metric to analyze (e.g., soundness, completeness).",
        choices=["sound", "complete", "exact matches"],
        required=False,
    )

    parser.add_argument(
        "--is_callsites",
        action="store_true",
        required=False,
    )

    return parser.parse_args()
