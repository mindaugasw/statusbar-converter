from unittest.mock import Mock

from src.Service.Configuration import Configuration
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
        configId: list[str],
    ) -> any:
        for configKey, configValue in overrides:
            if configKey == configId:
                return configValue

        for configKey, configValue in defaultConfig:
            if configKey == configId:
                return configValue

        raise Exception(f'configId "{configId}" not found in Configuration mock')
