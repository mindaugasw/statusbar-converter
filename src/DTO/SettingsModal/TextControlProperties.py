from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties


class TextControlProperties(AbstractControlProperties):
    castToType: type

    def __init__(self, configId: ConfigParameter, castToType: type):
        super().__init__(configId)

        self.castToType = castToType
