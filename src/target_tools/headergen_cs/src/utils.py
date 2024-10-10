import os

import json
import os
import re
import shutil
import sys
import requests
import logging

TOOL = "pycg"


def setup_logger(logger_name=f"{TOOL}_runner"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers to prevent adding duplicate ones
    if not logger.handlers:
        if is_running_in_docker():
            file_handler = logging.FileHandler(
                f"/tmp/{TOOL}_callgraph_log.log", mode="w"
            )
        else:
            file_handler = logging.FileHandler(f"{TOOL}_callgraph_log.log", mode="w")

        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def is_running_in_docker():
    """Check if Python is running inside a Docker container."""
    return (
        os.path.exists("/.dockerenv")
        or os.environ.get(  # Check if the /.dockerenv file exists
            "DOCKER_CONTAINER", False
        )
        or os.environ.get(  # Check if DOCKER_CONTAINER environment variable is set
            "DOCKER_IMAGE_NAME", False
        )  # Check if DOCKER_IMAGE_NAME environment variable is set
    )
