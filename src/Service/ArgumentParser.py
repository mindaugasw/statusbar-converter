import argparse

from src.Service.CLIArgsCreator import CLIArgsCreator


class ArgumentParser:
    _arguments: argparse.Namespace

    def __init__(self):
        parser = argparse.ArgumentParser()
        argsCreator = CLIArgsCreator(parser)

        argsCreator.addOptionBool('--debug', 'Enable more verbose logging')

        argsCreator.addOptionString(
            cliName='--mock-update',
            help='Helper for development. Allows mocking update check. Should be used to avoid GitHub rate limiter.',
            choices=['old', 'new'],
        )

        argsCreator.addOptionBool(
            '--mock-packaged',
            'Helper for development. Allows mocking in-development app as if it was running as packaged '
            '("frozen"). Can be used for autostart testing.',
        )

        argsCreator.addOptionString(
            '--currency-rates-url',
            'Override URL for currency conversion rates update',
        )

        argsCreator.addOptionInt(
            '--sleep',
            'Sleep this number of seconds before showing app icon',
        )
        """
        Sleep argument is needed for Linux, to make statusbar icon appear at the end, after
        all other icons. But in startup configuration you can't do "sleep 30 && /app/path",
        so instead we sleep inside the app
        """

        self._arguments = parser.parse_args()

    def isDebugEnabled(self) -> bool:
        return self._arguments.debug

    def getMockUpdate(self) -> str | None:
        return self._arguments.mock_update

    def getMockPackaged(self) -> bool:
        return self._arguments.mock_packaged

    def getCurrencyRatesUrl(self) -> str | None:
        return self._arguments.currency_rates_url

    def getSleep(self) -> int | None:
        return self._arguments.sleep
