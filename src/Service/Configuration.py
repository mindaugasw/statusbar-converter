import yaml
from src.Service.ConfigFileManager import ConfigFileManager


class Configuration:
    # Config keys
    CLEAR_ON_CHANGE = 'clear_on_change'
    CLEAR_AFTER_TIME = 'clear_after_time'
    FLASH_ICON_ON_CHANGE = 'flash_icon_on_change'
    FORMAT_ICON = 'format_icon'
    MENU_ITEMS_LAST_TIMESTAMP = 'menu_items_last_timestamp'
    MENU_ITEMS_CURRENT_TIMESTAMP = 'menu_items_current_timestamp'
    DEBUG = 'debug'

    _configFileManager: ConfigFileManager
    _configApp: dict
    """
    Default config of the application.
    Located in the project directory, should never be changed by the user.
    """
    _configUser: dict
    """
    User overrides of app config.
    Located in user temp files directory, can be changed by the user.
    """
    _configInitialized = False

    def __init__(self, configFileManager: ConfigFileManager):
        self._configFileManager = configFileManager

    def get(self, key: str):
        self._initializeConfig()

        userValue = self._queryConfigDictionary(key, self._configUser)

        if userValue is not None:
            return userValue

        return self._queryConfigDictionary(key, self._configApp)

    def _initializeConfig(self) -> None:
        if self._configInitialized:
            return

        self._configApp = yaml.load(
            self._configFileManager.getAppConfigContent(),
            yaml.Loader,
        )

        self._configUser = yaml.load(
            self._configFileManager.getUserConfigContent(),
            yaml.Loader,
        )

        self._configInitialized = True

    def _queryConfigDictionary(self, key: str, config: dict):
        if config is None:
            return None

        return config.get(key)
