from nikhil.amsha.output_process.validation import CrewConfigValidator
from nikhil.vak.utils.yaml_utils import YamlUtils

if __name__ == '__main__':
    config = YamlUtils().yaml_safe_load("config/validation_config.yaml")
    validator = CrewConfigValidator()
    validation_report = validator.validate(config.get("domain_root_path"), config.get("output_dir_path"))