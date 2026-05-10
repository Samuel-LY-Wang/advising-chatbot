import json
import os

def load_config():
    """
    Loads the config file from config.json. May add additional logic later for commonly used constants that can't be hard-coded (currently just cwd)
    """
    with open("config.json", "r") as f:
        config = json.load(f)
    config["cwd"] = os.getcwd()
    return config