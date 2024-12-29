from unittest.mock import Mock

from src.Service.Configuration import Configuration


class MockLibrary:
    @staticmethod
    def getConfig(configs: list[tuple[list[str], any]]) -> Configuration:
        def getSideEffect(configSetup: list[tuple[list[str], any]], configId: list[str]) -> any:
            for configKey, configValue in configSetup:
                if configKey == configId:
                    return configValue

            raise Exception(f'configId "{configId}" not found in Configuration mock')

        configMock = Mock(Configuration)
        configMock.get.side_effect = lambda configId: getSideEffect(configs,configId)

        return configMock
