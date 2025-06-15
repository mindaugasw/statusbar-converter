from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties


class CheckboxControlProperties(AbstractControlProperties):
    def __init__(self, configId: ConfigParameter):
        super().__init__(configId)
