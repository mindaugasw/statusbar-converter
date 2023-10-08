import yaml
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.ConfigFileManager import ConfigFileManager


class Configuration:
    # Config keys
    CLEAR_ON_CHANGE = ['clear_on_change']
    CLEAR_AFTER_TIME = ['clear_after_time']
    FLASH_ICON_ON_CHANGE = ['flash_icon_on_change']
    DEBUG = ['debug']
    FORMAT_ICON = ['converters', 'timestamp', 'icon_text_format']
    MENU_ITEMS_LAST_TIMESTAMP = ['converters', 'timestamp', 'menu_items_last_timestamp']
    MENU_ITEMS_CURRENT_TIMESTAMP = ['converters', 'timestamp', 'menu_items_current_timestamp']

    # Data keys
    DATA_UPDATE_SKIP_VERSION = ['update', 'skip_version']
    DATA_AUTO_RUN_INITIAL_SETUP_COMPLETE = ['auto_run', 'initial_setup_complete']

    _configFileManager: ConfigFileManager
    _appVersion: str
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
    _stateData: dict
    """
    App internal state.
    Writable by the app itself and should not be modified by the user
    """
    _configInitialized = False

    def __init__(self, configFileManager: ConfigFileManager):
        self._configFileManager = configFileManager

    def get(self, key: list[str]):
        self._initializeConfig()
        userValue = self._queryDictionary(key, self._configUser)

        if userValue is not None:
            return userValue

        return self._queryDictionary(key, self._configApp)

    def getState(self, key: list[str]):
        self._initializeConfig()

        return self._queryDictionary(key, self._stateData)

    def setState(self, key: list[str], value) -> None:
        self._setValue(key, value, self._stateData)

        stateContent = yaml.dump(self._stateData)
        stateContent = '# Internal app state. This file should not be edited manually.\n' + stateContent

        self._configFileManager.writeStateData(stateContent)

    def getAppVersion(self) -> str:
        self._initializeConfig()

        return self._appVersion

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

        self._stateData = yaml.load(
            self._configFileManager.getStateDataContent(),
            yaml.Loader,
        )

        with open(FilesystemHelper.getProjectDir() + '/version', 'r') as versionFile:
            self._appVersion = versionFile.read().strip()

        self._configInitialized = True

    def _queryDictionary(self, key: list[str], config: dict):
        if config is None:
            return None

        valuePartial = config

        for keyPartial in key:
            valuePartial = valuePartial.get(keyPartial)

            if valuePartial is None:
                return None

        return valuePartial

    def _setValue(self, key: list[str], value, config: dict) -> None:
        configPath = config

        for i, keyPartial in enumerate(key):
            if i == len(key) - 1:
                configPath[keyPartial] = value

                return

            newConfigPath = configPath.get(keyPartial)

            if newConfigPath is None:
                configPath[keyPartial] = {}
                newConfigPath = configPath[keyPartial]

            configPath = newConfigPath
