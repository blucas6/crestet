import config
import logger
import json

class Generator:

    def __init__(self):
        self.total_levels = 0
        self.data = None

    def load_config(self):
        try:
            with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
                self.data = json.load(jfile)

            self.total_levels = self.data['otal_levels']
        except Exception as ex:
            logger.Logger.log(f'Error while parsing: {ex}')
            raise

