import logging


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
