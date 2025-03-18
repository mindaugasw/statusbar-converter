from typing import Type

from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties


class SimpleControlProperties(AbstractControlProperties):
    """Suitable for Checkbox and Text input types"""

    castToType: Type

    def __init__(self, configId: ConfigParameter, castToType: Type):
        super().__init__(configId)

        self.castToType = castToType
