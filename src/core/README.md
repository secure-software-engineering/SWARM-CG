# Core Module

## Overview

The `core` module provides basic utilities and configurations for the application. It includes logging setup, configuration management, and other services that can be used throughout the application.

### Files

### `__init__.py`
Marks the directory as a Python package and can be used to initialize the `core` module or expose important functionality.

### `base_runner.py`
Contains the `BaseRunner` class, which provides a base implementation for running various tools. It includes common methods that can be overridden by specific tool runners.

### `config.py`
Handles loading configuration settings from a YAML file. Provides a `load_config` function to read and parse configuration data.

### `logger.py`
Sets up the logging configuration for the application. Provides the `setup_logger` function to configure logging for console and file outputs.

