import config
import json

class Generator:

    def __init__(self):
        with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
            data = json.load(jfile)
