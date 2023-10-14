import argparse


class ArgumentParser:
    _arguments: argparse.Namespace

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--sleep', type=int, help='Sleep this number of seconds before showing app icon')
        """
        Sleep argument is needed for Linux, to make statusbar icon appear at the end, after
        all other icons. But in startup configuration you can't do "sleep 30 && /app/path",
        so instead we sleep inside the app
        """

        self._arguments = parser.parse_args()

    def isDebugEnabled(self) -> bool:
        return self._arguments.debug

    def getSleep(self) -> int | None:
        return self._arguments.sleep
