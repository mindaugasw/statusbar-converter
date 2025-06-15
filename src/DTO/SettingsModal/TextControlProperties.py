from typing import Type

from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties


class TextControlProperties(AbstractControlProperties):

    castToType: Type

    def __init__(self, configId: ConfigParameter, castToType: Type):
        super().__init__(configId)

        self.castToType = castToType
