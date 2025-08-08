import yaml


class YamlUtils:

    @staticmethod
    def yaml_safe_load(config_file_path:str):
        with open(config_file_path, "r") as file:
            return yaml.safe_load(file)