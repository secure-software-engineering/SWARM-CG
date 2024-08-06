# CLI Module

The CLI module provides a command-line interface for running micro-benchmarks and analyzing results. It is designed to be modular and easily extendable to accommodate new features and options.


## Files

- **`cli_runner.py`**: Handles CLI arguments for running benchmarks. It includes options to specify the language of the micro-benchmarks, the target tool to use, and the models to test.

- **`cli_analyzer.py`**: Handles CLI arguments for analyzing benchmark results. It includes options to specify the results directory and output file for the analysis report.

- **`cli_utils.py`**: Contains utility functions used by the CLI, such as argument validation.
