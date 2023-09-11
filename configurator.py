import json
import logging

logging.basicConfig(filename='log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s | %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')


class Configurator:
    def __init__(self):
        # Hard coded values if config file doesn't exist
        self.hot_key_state: bool = False
        self.def_hot_key: str = 'CTRL + ALT + C'
        self.cust_hot_key: str = ''

    def __str__(self):
        return f'Custom Hotkey: {self.hot_key_state} \nDefault Value: {self.def_hot_key} \nCustom Value: {self.cust_hot_key}'

    def read_config_file(self, config_file_name: str = "config.json"):
        try:
            with open(config_file_name) as conf_file:
                data = json.load(conf_file)
                for key, value in data.items():
                    setattr(self, key, value)
        except Exception as e:
            logging.info(f"{str(e)} \n- File will be created and hard coded values will be applied. ")

    def save_config_file(self, config_file_name: str = "config.json"):
        try:
            conf_items = {k: v for k, v in vars(self).items() if isinstance(v, (int, float, str, bool, list, dict))}
            with open(config_file_name, "w") as conf_file:
                json.dump(conf_items, conf_file, sort_keys=False, indent=2)
        except Exception as e:
            logging.error(f"{str(e)} \n- Error occurred while saving: {config_file_name}")

    def get_value(self, key):
        """Extracts a specific key-value pair from the class attributes"""
        return getattr(self, key, None)

    def create_on_start(self):
        self.read_config_file()
        self.save_config_file()
