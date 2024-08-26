import logging
import os
import json

logger = logging.getLogger(__name__)


def setup_result_analysis_logging():
    """
    Set up a logger for the result analysis module.

    This function configures the logging system to log messages to both the console
    and a file with a basic format.
    """
    logger = logging.getLogger("Result Analysis")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("results_analysis.log")
    file_handler.setLevel(logging.DEBUG)

    file_handler_info = logging.FileHandler("results_analysis_info.log")
    file_handler_info.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    file_handler_info.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    if not logger.handlers:  # To avoid adding multiple handlers
        logger.addHandler(file_handler)
        logger.addHandler(file_handler_info)
        logger.addHandler(console_handler)
    return logger


def get_subdirs(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]


def do_sorted(d):
    return {str(n): sorted(d[n]) for n in d}


def load_json(file_path):
    """
    Load JSON data from a file with logging for errors.

    :param file_path: Path to the JSON file.
    :return: Data loaded from the JSON file, or an empty dictionary if an error occurs.
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {}
