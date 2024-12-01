import json
import platform
import threading
import time
import webbrowser
from typing import Callable

import requests

import src.events as events
from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class UpdateManager:
    CHECK_INTERVAL = 3600 * 24 * 2  # Check every 2 days
    RELEASES_URL = 'https://api.github.com/repos/mindaugasw/statusbar-converter/releases?per_page=100'

    _filesystemHelper: FilesystemHelper
    _config: Configuration
    _logger: Logger
    _debug: Debug

    _currentVersion: tuple[int, ...]
    _skippedVersion: tuple[int, ...] | None
    _lastCheckAt: int | None = None

    def __init__(self, filesystemHelper: FilesystemHelper, config: Configuration, logger: Logger, debug: Debug):
        self._filesystemHelper = filesystemHelper
        self._config = config
        self._logger = logger
        self._debug = debug

        events.appLoopIteration.append(self._updateCheckIteration)

    def checkForUpdatesAsync(self, manuallyTriggered: bool) -> None:
        self._lastCheckAt = int(time.time())
        threading.Thread(target=self._checkForUpdates, args=[manuallyTriggered], daemon=True).start()

    def _updateCheckIteration(self) -> None:
        if self._lastCheckAt and (int(time.time()) - self.CHECK_INTERVAL) < self._lastCheckAt:
            return

        self.checkForUpdatesAsync(False)

    def _checkForUpdates(self, manuallyTriggered: bool) -> None:
        self._logger.log(f'{Logs.catUpdateCheck}Starting check for updates, manual check: {manuallyTriggered}')

        if manuallyTriggered:
            self._logger.log(f'{Logs.catUpdateCheck}Clearing skipped version state')
            self._config.setState(Configuration.DATA_UPDATE_SKIP_VERSION, None)

        currentVersion = self._stringToVersionTuple(self._config.getAppVersion())
        skippedVersion = self._config.getState(Configuration.DATA_UPDATE_SKIP_VERSION)

        if skippedVersion is None:
            skippedVersion = (-1, -1, -1)
        else:
            skippedVersion = self._stringToVersionTuple(skippedVersion)

        releases = self._queryReleases()
        newUpdateFound = False

        for release in releases:
            if not self._isNewerVersion(release, currentVersion, skippedVersion):
                self._logger.log(
                    f'{Logs.catUpdateCheck}Release {release["tag_name"]} is old version or marked as skipped,'
                    f' stopping update check',
                )

                break

            if not self._doesReleaseContainCurrentPlatform(release):
                self._logger.log(f'{Logs.catUpdateCheck}Release {release["tag_name"]} does not contain current platform download')

                continue

            self._logger.log(f'{Logs.catUpdateCheck}Found a new release {release["tag_name"]}')
            newUpdateFound = True
            self._dispatchUpdateResultEvent(release['tag_name'])

            break

        if manuallyTriggered and not newUpdateFound:
            self._dispatchUpdateResultEvent(None)

        self._lastCheckAt = int(time.time())
        self._logger.log(f'{Logs.catUpdateCheck}Completed')

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

    def _queryReleases(self):
        mockUpdate = self._debug.getMockUpdate()

        if mockUpdate is not None:
            """
            Allow using mock response. Because GitHub has rate limiting per IP, which is possible to reach
            when testing more intensively
            """
            with open(f'{self._filesystemHelper.getAssetsDevDir()}/releases_response_mock_{mockUpdate}.json') as file:
                return json.load(file)

        return requests.get(self.RELEASES_URL).json()

    def _dispatchUpdateResultEvent(self, version: str | None) -> None:
        def _handleClickGoToDownloadPage() -> None:
            self._logger.log(f'{Logs.catUpdateCheck}Dialog button click: Go to download page')
            downloadPageUrl = f'{AppConstant.website}/releases/tag/{version}'
            webbrowser.open(downloadPageUrl)

        def _handleClickSkipThisVersion() -> None:
            self._logger.log(f'{Logs.catUpdateCheck}Dialog button click: Skip this version')
            self._config.setState(Configuration.DATA_UPDATE_SKIP_VERSION, version)

        def _handleClickRemindMeLater() -> None:
            self._logger.log(f'{Logs.catUpdateCheck}Dialog button click: Remind me later')

        text: str
        buttons: dict[str, Callable | None]

        if version is None:
            text = \
                f'No new version found.\n' \
                f'Current app version is v{self._config.getAppVersion()}.'

            buttons = {'Ok': None}
        else:
            text =\
                f'New app update found: {version}.\n' \
                f'Current app version is v{self._config.getAppVersion()}.\n' \
                f'Release notes available on the download page.\n\n' \
                f'Download update?'

            buttons = {
                'Go to download page': _handleClickGoToDownloadPage,
                'Skip this version': _handleClickSkipThisVersion,
                'Remind me later': _handleClickRemindMeLater,
            }

        events.updateCheckCompleted(text, buttons)
