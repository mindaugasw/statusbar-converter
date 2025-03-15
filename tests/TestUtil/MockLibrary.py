from typing import Any
from unittest.mock import Mock

from src.DTO.ConfigParameter import ConfigParameter
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
        configId: ConfigParameter,
    ) -> Any:
        for configParam, configValue in overrides:
            if configParam.key == configId.key:
                return configValue

        for configParam, configValue in defaultConfig:
            if configParam.key == configId.key:
                return configValue

        raise Exception(f'configId "{configId.key}" not found in Configuration mock')
