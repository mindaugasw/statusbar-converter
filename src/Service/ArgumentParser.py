import argparse


class ArgumentParser:
    _arguments: argparse.Namespace

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--debug', action='store_true', help='Enable more verbose logging')
        parser.add_argument('--mock-update', action='store', help='Helper for development. Allows mocking update check. Value must be one of ["old", "new"]')
        parser.add_argument('--mock-packaged', action='store_true', help='Helper for development. Allows mocking in-development app as if it was running as packaged ("frozen"). Can be used for autostart testing.')
        parser.add_argument('--sleep', type=int, help='Sleep this number of seconds before showing app icon')
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

    def getSleep(self) -> int | None:
        return self._arguments.sleep
