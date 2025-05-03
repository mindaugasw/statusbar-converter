from typing import Any

import yaml

from src.Constant.Logs import Logs
from src.DTO.ConfigParameter import ConfigParameter
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
    Located in user files directory, can be changed by the user.
    """

    _state: dict
    """
    App internal state.
    Writable by the app itself and should not be modified by the user (but there are no protections against it)
    """

    _configInitialized: bool

    def __init__(self, configFileManager: ConfigFileManager, logger: Logger):
        self._configFileManager = configFileManager
        self._logger = logger

        self._configInitialized = False

    def getAppVersion(self) -> str:
        self._initializeConfig()

        return self._appVersion

    def get(self, parameter: ConfigParameter) -> Any:
        self._initializeConfig()

        if parameter.isState:
            return self._getStateParameter(parameter.key, parameter.defaultValue)
        else:
            return self._getConfigParameter(parameter.key)

    def set(self, parameter: ConfigParameter, value: Any) -> None:
        self._initializeConfig()

        if not parameter.isState:
            raise Exception(
                f'Cannot persist ConfigParameter that is not "state" stype {parameter.getKeyString()}',
            )

        self._setState(parameter.key, value)

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

        self._state = yaml.load(
            self._configFileManager.getStateDataContent(),
            yaml.Loader,
        )

        with open(FilesystemHelper.getProjectDir() + '/version', 'r') as versionFile:
            self._appVersion = versionFile.read().strip()

        self._configInitialized = True

    def _getConfigParameter(self, key: list[str]) -> Any:
        userValue = self._queryDictionary(key, self._configUser)

        if userValue is not None:
            return userValue

        return self._queryDictionary(key, self._configApp)

    def _getStateParameter(self, key: list[str], defaultValue: Any) -> Any:
        value = self._queryDictionary(key, self._state)

        if value is None and defaultValue is not None:
            # If we return default value, that means for whatever reason it does
            # not exist in the file. So we write that value even on "get" action.
            self._logger.log(
                f'{Logs.catConfig}Missing state value {self._keyString(key)} in file. '
                f'Will persist given default value: {defaultValue}',
            )

            self._setState(key, defaultValue)
            value = defaultValue

        return value

    def _queryDictionary(self, key: list[str], config: dict):
        if config is None:
            return None

        valuePartial = config

        for keyPartial in key:
            valuePartial = valuePartial.get(keyPartial)  # type: ignore[assignment]

            if valuePartial is None:
                return None

        return valuePartial

    def _setState(self, key: list[str], value: Any) -> None:
        self._logger.log(f'{Logs.catConfig}Persisting state: {self._keyString(key)}: {value}')
        self._setValue(key, value, self._state)

        stateContent = yaml.dump(self._state)
        stateContent = '# Internal app state. THIS FILE SHOULD NOT BE EDITED MANUALLY.\n\n' + stateContent

        self._configFileManager.writeStateData(stateContent)

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

    def _keyString(self, key: list[str]) -> str:
        return '[' + '.'.join(key) + ']'
