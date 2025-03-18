from abc import ABC

from src.DTO.ConfigParameter import ConfigParameter


class AbstractControlProperties(ABC):
    configId: ConfigParameter

    def __init__(self, configId: ConfigParameter):
        self.configId = configId
