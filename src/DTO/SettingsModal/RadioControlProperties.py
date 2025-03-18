from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties
from src.Type.Types import SettingsRadioValues


class RadioControlProperties(AbstractControlProperties):
    radioValues: SettingsRadioValues

    def __init__(self, configId: ConfigParameter, radioValues: SettingsRadioValues):
        super().__init__(configId)

        self.radioValues = radioValues
