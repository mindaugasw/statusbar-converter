from unittest.mock import Mock

from src.Service.Configuration import Configuration


class MockLibrary:
    @staticmethod
    def getConfig(configs: list[tuple[list[str], any]]) -> Configuration:
        def getSideEffect(configId: list[str]) -> any:
            for configKey, configValue in configs:
                if configKey == configId:
                    return configValue

            raise Exception(f'configId "{configId}" not found in Configuration mock')

        configMock = Mock(Configuration)
        configMock.get.side_effect = getSideEffect

        return configMock
