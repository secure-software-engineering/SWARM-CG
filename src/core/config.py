import yaml
import os

def load_config(config_file):
    """Load configuration from a YAML file."""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} does not exist.")  
    with open(config_file, "r") as file:
        config = yaml.safe_load(file) 
    return config
