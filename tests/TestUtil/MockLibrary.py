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
        mock.getProjectDir.return_value = '/home/username/Projects/statusbar-converter'
        mock.getInitializationLogs.return_value = '[Init logs]'
        mock.getAssetsDir.return_value = mock.getProjectDir() + '/assets'
        mock.getAssetsDevDir.return_value = mock.getProjectDir() + '/assets_dev'
        mock.getConfigDir.return_value = mock.getProjectDir() + '/config'
        mock.getBinariesDir.return_value = mock.getProjectDir() + '/binaries'
        mock.getAppExecutablePath.return_value = '/home/username/Apps/Statusbar Converter'
        mock.getStartupScriptDir.return_value = '/home/username/.config/autostart'
        mock.isPackagedApp.return_value = True
        mock.openFile.return_value = None

        return mock
