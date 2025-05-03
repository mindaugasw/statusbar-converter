from typing import Any


class ConfigParameter:
    key: list[str]
    isState: bool
    defaultValue: Any

    @staticmethod
    def newConfig(key: list[str]) -> 'ConfigParameter':
        configParameter = ConfigParameter()
        configParameter.key = key
        configParameter.isState = False

        # "Config" type has fallback to default config file, so defaultValue here is not needed

        return configParameter

    @staticmethod
    def newState(key: list[str], defaultValue: Any) -> 'ConfigParameter':
        configParameter = ConfigParameter()
        configParameter.key = key
        configParameter.isState = True
        configParameter.defaultValue = defaultValue

        return configParameter

    def getKeyString(self) -> str:
        return '[' + '.'.join(self.key) + ']'
