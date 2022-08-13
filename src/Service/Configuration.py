import yaml
from src.Service.ConfigFileManager import ConfigFileManager


class Configuration:
    # Config keys
    TIMESTAMP_MIN = 'timestamp_min'
    TIMESTAMP_MAX = 'timestamp_max'
    CLEAR_ON_CHANGE = 'clear_on_change'
    CLEAR_AFTER_TIME = 'clear_after_time'
    FLASH_ICON_ON_CHANGE = 'flash_icon_on_change'
    CLIPBOARD_POLLING_INTERVAL = 'clipboard_polling_interval'
    FORMAT_ICON = 'format_icon'
    MENU_ITEMS_LAST_TIMESTAMP = 'menu_items_last_timestamp'
    MENU_ITEMS_CURRENT_TIMESTAMP = 'menu_items_current_timestamp'
    DEBUG = 'debug'

    _configFileManager: ConfigFileManager
    _configGlobal: dict
    _configLocal: dict
    _configInitialized = False

    def __init__(self, configFileManager: ConfigFileManager):
        self._configFileManager = configFileManager

    def get(self, key: str):
        self._initializeConfig()

        localValue = self._getFromConfigData(key, self._configLocal)

        if localValue is not None:
            return localValue

        return self._getFromConfigData(key, self._configGlobal)

    def _initializeConfig(self) -> None:
        if self._configInitialized:
            return

        globalConfigContent = self._configFileManager.getGlobalConfigContent()
        self._configGlobal = yaml.load(globalConfigContent, yaml.Loader)

        localConfigContent = self._configFileManager.getLocalConfigContent()
        self._configLocal = yaml.load(localConfigContent, yaml.Loader)

        self._configInitialized = True

    def _getFromConfigData(self, key: str, config: dict):
        if config is None:
            return None

        return config.get(key)
