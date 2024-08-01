import logging

def setup_logger(log_name, log_file):
    """Set up logging configuration.
    
    This function configures the logging system to log messages to both the console
    and a file with a basic format.
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    if not logger.handlers:  # To avoid adding multiple handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger