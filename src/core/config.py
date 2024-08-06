import yaml

def load_config(config_file):
    """
    Load a YAML configuration file.
    """
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config
