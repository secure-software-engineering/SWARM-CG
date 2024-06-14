import logging
from pathlib import Path
from datetime import datetime

# create .logs folder if it doesn't exist
Path(__file__).parent.parent.parent.joinpath(".log").mkdir(exist_ok=True)

LOGGING_FILE = Path(__file__).parent.parent.parent / ".log" / f"swarm-cg-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"


def setup_logging(name):
    # Creating a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(LOGGING_FILE, mode="w")

    # Set level for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Create and set formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False  # otherwise root logger prints things again
    return logger
