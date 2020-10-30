from ._configuration import Configuration
from objects import TypeList


class ConfigurationDictionary(object):
    def __init__(self) -> None:
        self.configurations: TypeList = TypeList(Configuration)

    def add_configuration(self, configuration: Configuration) -> None:
        self.configurations.append(configuration)

    @property
    def get_configurations(self) -> TypeList:
        return self.configurations

    @property
    def get_configurations_dict(self) -> dict:
        result: dict = {}

        configuration: Configuration
        for configuration in self.configurations:
            result[configuration.name] = {
                "set": configuration.get_set_function,
                "add": configuration.get_add_function,
                "remove": configuration.get_remove_function,
                "config_name": configuration.config_name
            }

        return result
