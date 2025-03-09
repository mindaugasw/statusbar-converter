import os

from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManagerV2 import AutostartManagerV2
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class AutostartManagerV2MacOS(AutostartManagerV2):
    # Login items scripting via Apple script source/reference:
    # https://gist.github.com/nweddle/e8cece424a8c8c1e121ad33922dc7dd0

    def __init__(
        self,
        filesystemHelper: FilesystemHelper,
        config: Configuration,
        argParser: ArgumentParser,
        logger: Logger,
    ):
        super().__init__(filesystemHelper, config, argParser, logger)

    def _enableAutostartOsSpecific(self) -> str | None:
        command = 'osascript -e \'tell application "System Events" to make login item at end ' \
                  f'with properties {{path:"{self._appExecutablePath}", hidden:false}}\' 2>&1'
        output = os.popen(command).read().strip()

        return output

    def _disableAutostartOsSpecific(self) -> str | None:
        executableName = self._appExecutablePath.split('/')[-1]
        command = f'osascript -e \'tell application "System Events" to delete login item "{executableName}"\' 2>&1'
        output = os.popen(command).read().strip()

        return output

    def _validateSetup(self) -> bool:
        # macOS seems to be quite good at automatically managing login item changes
        # (e.g. automatically updating on file move/delete). So if login item will
        # be missing, it's likely user has deleted it from the Settings app.
        # So we skip validating setup and attempting to auto-repair it, to respect
        # possible intentional disabling by the user.

        # If needed to validate in the future:
        # search for executable path in the output of this command:
        # os.popen('osascript -e \'tell application "System Events" to get the properties of every login item\'').read()

        return True

