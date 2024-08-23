import os
from pathlib import Path
from cli import parse_analyzer_args  # Import the argument parsing function
from analyzer import (
    setup_result_analysis_logging,
    data_loader,
    analysis_metrics,
    analysis_tables,
)


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


def main(results_dir=None, output_dir=None, analyze_metric=None):

    # Set up logging for the analyzer
    logger = setup_result_analysis_logging()
    logger.info("Result Analysis Started\n")

    if results_dir is None:
        dir_path = Path(SCRIPT_DIR) / "../results"
        directories = [
            f
            for f in dir_path.iterdir()
            if f.is_dir() and f.name.startswith("results_")
        ]
        directories.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        # Get the latest directory
        results_dir = directories[0] if directories else None
    else:
        results_dir = Path(results_dir)

    if output_dir is None:
        output_dir = results_dir / "analysis_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    tools_results = {}

    # Load data
    for model_dir in sorted(results_dir.glob("*")):
        if model_dir.is_dir():
            logger.info(f"Analyzing model: {model_dir.name}")
            tools_results[model_dir.name] = {}

            # Perform the analysis based on the metric or all if none specified
            data = data_loader.load_data(model_dir)
            if analyze_metric:
                tools_results[model_dir.name][analyze_metric] = (
                    analysis_metrics.calculate_metric(data, analyze_metric)
                )
            else:
                tools_results[model_dir.name]["soundness"] = (
                    analysis_metrics.calculate_soundness(data)
                )
                tools_results[model_dir.name]["completeness"] = (
                    analysis_metrics.calculate_completeness(data)
                )
    # Generate tables
    analysis_tables.generate_all_tables(tools_results, output_dir)

    # Save results
    logger.info(f"Analysis completed. Results saved in {output_dir}")


if __name__ == "__main__":
    args = parse_analyzer_args()  # Call the function to parse arguments
    main(args.results_dir, args.output_dir, args.analyze_metric)
