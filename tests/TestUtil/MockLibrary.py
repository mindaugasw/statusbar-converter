from typing import Any
from unittest.mock import Mock

from src.DTO.ConfigParameter import ConfigParameter
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from tests.TestUtil.Types import ConfigurationsList


class MockLibrary:
    @staticmethod
    def getConfig(
        defaultConfig: ConfigurationsList,
        overrides: ConfigurationsList | None = None,
    ) -> Configuration:
        if overrides is None:
            overrides = []

        configMock = Mock(Configuration)
        configMock.get.side_effect =\
            lambda configId: MockLibrary._configGetSideEffect(defaultConfig, overrides, configId)

        return configMock

    @staticmethod
    def _configGetSideEffect(
        defaultConfig: ConfigurationsList,
        overrides: ConfigurationsList,
        configId: ConfigParameter,
    ) -> Any:
        for configParam, configValue in overrides:
            if configParam.key == configId.key:
                return configValue

        for configParam, configValue in defaultConfig:
            if configParam.key == configId.key:
                return configValue

        raise Exception(f'configId {configId.getKeyString()} not found in Configuration mock')

    @staticmethod
    def getFilesystemHelper() -> FilesystemHelper:
        mock = Mock(FilesystemHelper)
        mock.getUserDataDir.return_value = '/home/username/.config/Statusbar Converter'
        # TODO would be nice to mock all methods, to avoid misusing later on. For that need to convert class to non-static
        return mock
