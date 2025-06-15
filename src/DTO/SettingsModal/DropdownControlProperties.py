from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties


class DropdownControlProperties(AbstractControlProperties):
    nameToValueMap: dict[str, str]

    def __init__(self, configId: ConfigParameter, nameToValueMap: dict[str, str]):
        super().__init__(configId)

        self.nameToValueMap = nameToValueMap
