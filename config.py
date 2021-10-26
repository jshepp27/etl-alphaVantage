import json
import os
import logging
from dataclasses import dataclass
from typing import Optional

basedir = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger(__name__)


@dataclass
class ConfigItem:
    name: str
    environment_variable: str
    config_file_key: str
    default_value: Optional[str] = None


class ConfigurationError(IOError):
    pass


class Config:
    def __init__(self, *args):
        self._config_items = {}
        for arg in args:
            if not isinstance(arg, ConfigItem):
                raise TypeError(
                    f"Config takes only ConfigItem objects as arguments. {arg.__class__.__name___} was provided.")
            logger.info(f"Adding {arg.name} to configuration setup.")
            self._config_items[arg.name] = arg
        self._config_file_data = None

    def load_config(self, file_name="config.json"):
        try:
            with open(file_name) as file:
                logger.debug(f"Loading configuration from {file_name},")
                self._config_file_data = json.load(file)

        except IOError as e:
            # `from e` here guarantees that we provide the original error message as well as our own.
            raise ConfigurationError(f"Cannot open configuration file {file_name}.") from e

    def __getitem__(self, item: str):
        logger.debug(f"Getting {item} from configuration.")
        try:
            config_item = self._config_items[item]
            logger.debug(f"Found {item} config_item in configuration.")
        except AttributeError as e:
            raise RuntimeError(f"No such configuration item: {item}") from e

        try:
            logger.debug(f"Attempting to find {config_item.environment_variable} in the environment.")
            return os.environ[config_item.environment_variable]
        except KeyError:
            """This is fine, it just means that there is no environment variable defined"""
            logger.debug(f"Failed to find {config_item.environment_variable} in the environment.")
            pass

        try:
            logger.debug(f"Attempting to find {config_item.config_file_key} in the config file.")
            return self._config_file_data[config_item.config_file_key]
        except (KeyError, TypeError):
            """This is fine, it just means that there is no such key in the config file"""
            logger.debug(f"Failed to find {config_item.config_file_key} in the config file.")
            pass

        if config_item.default_value:
            logger.debug(f"Falling back on default value: {config_item.default_value}.")
            return config_item.default_value

        raise RuntimeError(
            f"{item} has been requested from configuration, but is not defined in the environment or the config file, and has no default value set.")
