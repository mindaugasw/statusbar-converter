import json
import platform
import threading
import time
import webbrowser

import requests
from typing_extensions import Final

from src.Constant.AppConstant import AppConstant
from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.Exception.InvalidHTTPResponseException import InvalidHTTPResponseException
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.EventService import EventService
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Type.Types import DialogButtonsDict


class UpdateManager:
    _CHECK_INTERVAL: Final[int] = 3600 * 24 * 2  # Check every 2 days
    _RELEASES_URL: Final[str] = 'https://api.github.com/repos/mindaugasw/statusbar-converter/releases?per_page=100'

    _filesystemHelper: FilesystemHelper
    _events: EventService
    _config: Configuration
    _logger: Logger
    _debug: Debug

    _currentVersion: tuple[int, ...]
    _skippedVersion: tuple[int, ...] | None
    _lastCheckAt: int | None

    def __init__(
        self,
        filesystemHelper: FilesystemHelper,
        events: EventService,
        config: Configuration,
        logger: Logger,
        debug: Debug,
    ):
        self._filesystemHelper = filesystemHelper
        self._events = events
        self._config = config
        self._logger = logger
        self._debug = debug

        self._lastCheckAt = None
        self._events.subscribeAppLoopIteration(self._updateCheckIteration)

    def checkForUpdatesAsync(self, manuallyTriggered: bool) -> None:
        self._lastCheckAt = int(time.time())
        threading.Thread(target=self._checkForUpdates, args=[manuallyTriggered], daemon=True).start()

    def _updateCheckIteration(self) -> None:
        if self._lastCheckAt and (int(time.time()) - self._CHECK_INTERVAL) < self._lastCheckAt:
            return

        self.checkForUpdatesAsync(False)

    def _checkForUpdates(self, manuallyTriggered: bool) -> None:
        self._logger.log(f'{Logs.catUpdateCheck}Starting check for updates, manual check: {manuallyTriggered}')

        try:
            if manuallyTriggered:
                self._logger.log(f'{Logs.catUpdateCheck}Clearing skipped version state')
                self._config.set(ConfigId.Update_SkipVersion, None)

            currentVersion = self._stringToVersionTuple(self._config.getAppVersion())
            skippedVersion = self._config.get(ConfigId.Update_SkipVersion)

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
        except Exception as e:
            self._logger.log(f'{Logs.catUpdateCheck}UPDATE CHECK EXCEPTION:\n{ExceptionHandler.formatExceptionLog(e)}')

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

        response = requests.get(self._RELEASES_URL)
        statusCode = response.status_code

        if statusCode < 200 or statusCode > 299:
            raise InvalidHTTPResponseException('Received invalid response when checking for app updates', response)

        return response.json()

    def _dispatchUpdateResultEvent(self, version: str | None) -> None:
        def _handleClickGoToDownloadPage(foundVersion: str) -> None:
            self._logger.log(f'{Logs.catUpdateCheck}Dialog button click: Go to download page')
            downloadPageUrl = f'{AppConstant.WEBSITE}/releases/tag/{foundVersion}'
            webbrowser.open(downloadPageUrl)

        def _handleClickSkipThisVersion(versionToSkip: str) -> None:
            self._logger.log(f'{Logs.catUpdateCheck}Dialog button click: Skip this version')
            self._config.set(ConfigId.Update_SkipVersion, versionToSkip)

        def _handleClickRemindMeLater() -> None:
            self._logger.log(f'{Logs.catUpdateCheck}Dialog button click: Remind me later')

        text: str
        buttons: DialogButtonsDict

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
                'Go to download page': lambda: _handleClickGoToDownloadPage(version),
                'Skip this version': lambda: _handleClickSkipThisVersion(version),
                'Remind me later': lambda: _handleClickRemindMeLater(),
            }

        self._events.dispatchUpdateCheckCompleted(text, buttons)
