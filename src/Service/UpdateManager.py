import platform
import threading
import time

import requests

import src.events as events
from src.Service.Configuration import Configuration
from src.Service.Logger import Logger


class UpdateManager:
    CHECK_INTERVAL = 3600 * 24 * 2  # Check every 2 days
    RELEASES_URL = 'https://api.github.com/repos/mindaugasw/statusbar-converter/releases?per_page=100'

    _config: Configuration
    _logger: Logger

    _currentVersion: tuple[int, ...]
    _skippedVersion: tuple[int, ...] | None
    _lastCheckAt: int | None = None

    def __init__(self, config: Configuration, logger: Logger):
        self._config = config
        self._logger = logger

        events.appLoopIteration.append(self._updateCheckIteration)

    def checkForUpdatesAsync(self, manuallyTriggered: bool) -> None:
        self._lastCheckAt = int(time.time())
        threading.Thread(target=self._checkForUpdates, args=[manuallyTriggered], daemon=True).start()

    def _updateCheckIteration(self) -> None:
        if self._lastCheckAt and (int(time.time()) - self.CHECK_INTERVAL) < self._lastCheckAt:
            return

        self.checkForUpdatesAsync(False)

    def _checkForUpdates(self, manuallyTriggered: bool) -> None:
        self._logger.log(f'[Update check] Starting check for updates, manual check: {manuallyTriggered}')

        if manuallyTriggered:
            self._logger.log('[Update check] Clearing skipped version state')
            self._config.setState(Configuration.DATA_UPDATE_SKIP_VERSION, None)

        currentVersion = self._stringToVersionTuple(self._config.getAppVersion())
        skippedVersion = self._config.getState(Configuration.DATA_UPDATE_SKIP_VERSION)

        if skippedVersion is None:
            skippedVersion = (-1, -1, -1)
        else:
            skippedVersion = self._stringToVersionTuple(skippedVersion)

        releases = requests.get(self.RELEASES_URL).json()
        newUpdateFound = False

        for release in releases:
            if not self._isNewerVersion(release, currentVersion, skippedVersion):
                self._logger.log(
                    f'[Update check] Release {release["tag_name"]} is old version or marked as skipped,'
                    f' stopping update check',
                )

                break

            if not self._doesReleaseContainCurrentPlatform(release):
                self._logger.log(f'[Update check] Release {release["tag_name"]} does not contain current platform download')

                continue

            self._logger.log('[Update check] Found a new release ' + release['tag_name'])
            newUpdateFound = True
            events.updateCheckCompleted(release['tag_name'])

            break

        if manuallyTriggered and not newUpdateFound:
            events.updateCheckCompleted(None)

        self._lastCheckAt = int(time.time())
        self._logger.log('[Update check] Completed')

    def _isNewerVersion(
            self,
            release: dict,
            currentVersion: tuple[int, ...],
            skippedVersion: tuple[int, ...] | None,
    ) -> bool:
        releaseVersion = release['tag_name'].strip('v')
        releaseVersion = self._stringToVersionTuple(releaseVersion)

        if releaseVersion <= currentVersion:
            return False

        if releaseVersion <= skippedVersion:
            return False

        return True

    def _doesReleaseContainCurrentPlatform(self, release: dict) -> bool:
        os = 'macos' if platform.system() == 'Darwin' else 'linux'
        architecture = 'arm64' if platform.machine() == 'arm64' else 'x86_64'

        for asset in release['assets']:
            assetName = asset['name'].lower()

            if os in assetName and architecture in assetName:
                return True

        return False

    def _stringToVersionTuple(self, version: str) -> tuple[int, ...]:
        version = version.replace('v', '')

        # From https://stackoverflow.com/a/11887825/4110469
        return tuple(map(int, (version.split('.'))))

    def _suggestUpdate(self) -> None:
        pass
