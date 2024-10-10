import os
from pathlib import Path
from cli import parse_analyzer_args  # Import the argument parsing function
from result_analysis import (
    setup_result_analysis_logging,
    BaseAnalyzer,
)


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


def find_latest_results_dir():
    """
    Finds the latest results directory based on modification time.
    """
    dir_path = Path(SCRIPT_DIR) / "../results"
    directories = [
        f for f in dir_path.iterdir() if f.is_dir() and f.name.startswith("results_")
    ]
    # Sort directories by modification time, latest first
    directories.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return directories[0] if directories else None


def main(
    results_dir=None,
    analysis_results_dir=None,
    analysis_metric=None,
    is_callsites=False,
):

    # Set up logging for the analyzer
    logger = setup_result_analysis_logging()
    logger.info("Result Analysis Started\n")

    if results_dir is None:
        results_dir = find_latest_results_dir()
        if results_dir is None:
            logger.error("No results directory found.")
            return
        logger.info(f"Using latest results directory: {results_dir}")
    else:
        results_dir = Path(results_dir)

    if analysis_results_dir is None:
        analysis_results_dir = results_dir / "analysis_results"
    analysis_results_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Analysis results stored in: {analysis_results_dir}")

    analyzer = BaseAnalyzer(
        results_dir, analysis_results_dir, analysis_metric, is_callsites
    )
    analyzer.analyze()


if __name__ == "__main__":
    args = parse_analyzer_args()  # Call the function to parse arguments
    main(
        args.results_dir,
        args.analysis_output_dir,
        args.analysis_metric,
        args.is_callsites,
    )
