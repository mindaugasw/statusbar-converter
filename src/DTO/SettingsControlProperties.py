from typing import Type

from src.DTO.ConfigParameter import ConfigParameter


class SettingsControlProperties:
    configId: ConfigParameter
    castToType: Type

    def __init__(self, configId: ConfigParameter, castToType: Type):
        self.configId = configId
        self.castToType = castToType
