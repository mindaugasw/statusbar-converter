import threading
import time
import requests
import src.events as events
from src.Service.Configuration import Configuration
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Debug import Debug


class UpdateManager:
    CHECK_INTERVAL = 3600 * 24 * 3  # Check every 3 days
    RELEASES_URL = 'https://api.github.com/repos/mindaugasw/statusbar-converter/releases?per_page=100'

    _config: Configuration
    _debug: Debug

    _currentVersion: tuple[int, ...]
    _lastCheckAt: int | None = None

    def __init__(self, config: Configuration, filesystemHelper: FilesystemHelper, debug: Debug):
        self._config = config
        self._debug = debug

        with open(filesystemHelper.getProjectDir() + '/version', 'r') as currentVersionFile:
            currentVersionContent = currentVersionFile.read()
            # From https://stackoverflow.com/a/11887825/4110469
            self._currentVersion = tuple(map(int, (currentVersionContent.split('.'))))

        events.appLoopIteration.append(self._updateCheckIteration)

    def checkForUpdatesAsync(self) -> None:
        self._lastCheckAt = int(time.time())
        threading.Thread(target=self._checkForUpdates).start()

    def _updateCheckIteration(self) -> None:
        if self._lastCheckAt and (int(time.time()) - self.CHECK_INTERVAL) < self._lastCheckAt:
            return

        self.checkForUpdatesAsync()

    def _checkForUpdates(self) -> None:
        self._debug.log('Starting check for updates')
        # skippedVersion = self.

        releases = requests.get(self.RELEASES_URL).json()
        self._debug.log('sss')

        self._lastCheckAt = int(time.time())
