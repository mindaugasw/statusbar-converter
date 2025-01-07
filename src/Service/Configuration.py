import yaml

from src.Constant.Logs import Logs
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class Configuration:
    _configFileManager: ConfigFileManager
    _logger: Logger

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
    _configInitialized: bool

    def __init__(self, configFileManager: ConfigFileManager, logger: Logger):
        self._configFileManager = configFileManager
        self._logger = logger

        self._configInitialized = False

    def get(self, key: list[str]):
        self._initializeConfig()
        userValue = self._queryDictionary(key, self._configUser)

        if userValue is not None:
            return userValue

        return self._queryDictionary(key, self._configApp)

    def getState(self, key: list[str], default = None):
        self._initializeConfig()

        value = self._queryDictionary(key, self._stateData)

        if value is None and default is not None:
            # Since we will return a default value, depending on which other actions may happen,
            # we need to ensure it stays consistent. So we set value on "get" action
            self._logger.log(f'{Logs.catConfig}Missing state value {key} in file. Will persist given default value: {default}')

            self.setState(key, default)
            value = default

        return value

    def setState(self, key: list[str], value) -> None:
        self._logger.log(f'{Logs.catConfig}Persisting state: {key}: {value}')
        self._setValue(key, value, self._stateData)

        stateContent = yaml.dump(self._stateData)
        stateContent = '# Internal app state. THIS FILE SHOULD NOT BE EDITED MANUALLY.\n\n' + stateContent

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
