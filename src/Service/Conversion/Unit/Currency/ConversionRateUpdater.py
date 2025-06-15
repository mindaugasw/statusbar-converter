import hashlib
import json
import os.path
import platform
import threading
import time

import requests
from typing_extensions import Final

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.Converter.CurrenciesFileData import CurrenciesFileData
from src.DTO.Converter.CurrenciesRefreshResult import CurrenciesRefreshResult
from src.DTO.Exception.InvalidHTTPResponseException import InvalidHTTPResponseException
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Configuration import Configuration
from src.Service.Conversion.Unit.Currency.CurrencyConverter import CurrencyConverter
from src.Service.EventService import EventService
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.OSSwitch import OSSwitch


class ConversionRateUpdater:
    """
    Terms:
    refreshed_at - time of the actual rates, as returned by the API
    cached_at - when were rates retrieved and cached by my script
    parsed_at - when desktop application parsed data
    """

    _UPDATE_INTERVAL: Final[int] = 3600 * 3  # 3 hours

    _currencyConverter: CurrencyConverter
    _config: Configuration
    _events: EventService
    _osSwitch: OSSwitch
    _logger: Logger

    _url: str
    _ratesFilePath: str
    _lastOnlineRefreshAt: int | None
    _requestHeaders: dict[str, str]

    def __init__(
        self,
        currencyConverter: CurrencyConverter,
        filesystemHelper: FilesystemHelper,
        argumentParser: ArgumentParser,
        config: Configuration,
        events: EventService,
        osSwitch: OSSwitch,
        logger: Logger,
    ):
        self._currencyConverter = currencyConverter
        self._config = config
        self._events = events
        self._osSwitch = osSwitch
        self._logger = logger

        self._lastOnlineRefreshAt = None
        self._ratesFilePath = filesystemHelper.getUserDataDir() + '/currency_rates.json'

        urlOverride = argumentParser.getCurrencyRatesUrl()
        self._url = urlOverride if urlOverride is not None else config.get(ConfigId.Converter_Currency_RatesUrl)

    def initializeRatesAsync(self) -> None:
        # Here we don't skip rates update, even if currency converter is disabled.
        # That is needed to have currency list, to allow enabling converter in settings
        # and immediately select primary currency, instead of having to restart the app

        threading.Thread(target=self._initializeRates, daemon=True).start()

    def _initializeRates(self) -> None:
        fileResult = self._refreshFromLocalFile()

        self._logger.log(
            f'{Logs.catRateUpdater}Initialize - local refresh {"success" if fileResult.success else "FAIL"}, '
            f'isOutdated: {fileResult.isOutdated}, '
            f'cachedAt: {fileResult.data.cachedAt if fileResult.success else "-"}, '  # type: ignore[union-attr]
            f'refreshedAt: {fileResult.data.refreshedAt if fileResult.success else "-"}',  # type: ignore[union-attr]
        )

        parsedData: CurrenciesFileData | None = None
        onlineResult: CurrenciesRefreshResult | None = None

        if fileResult.success:
            parsedData = fileResult.data

        if fileResult.isOutdated:
            onlineResult = self._refreshFromOnline()

            if onlineResult.success:
                parsedData = onlineResult.data

        if fileResult.success and (onlineResult is None or not onlineResult.success):
            self._currencyConverter.refreshUnits(parsedData.currencies)  # type: ignore[union-attr]

        if self._config.get(ConfigId.Converter_Currency_Enabled):
            self._events.subscribeAppLoopIteration(self._updateCheck)

    def _refreshFromLocalFile(self) -> CurrenciesRefreshResult:
        try:
            if not os.path.isfile(self._ratesFilePath):
                return CurrenciesRefreshResult(False, True)

            with open(self._ratesFilePath, 'r') as file:
                text = file.read()
                parsedData = self._parseJsonText(text)
                isOutdated: bool

                if int(time.time()) - parsedData.cachedAt > self._UPDATE_INTERVAL:
                    isOutdated = True
                else:
                    isOutdated = False
                    self._lastOnlineRefreshAt = parsedData.cachedAt

                return CurrenciesRefreshResult(True, isOutdated, parsedData)
        except Exception as e:
            self._logger.log(
                f'{Logs.catRateUpdater}EXCEPTION in currency rates update - local file parsing:\n'
                f'{ExceptionHandler.formatExceptionLog(e)}',
            )

            return CurrenciesRefreshResult(False, True)

    def _refreshFromOnline(self) -> CurrenciesRefreshResult:
        self._lastOnlineRefreshAt = int(time.time())

        try:
            response = requests.get(self._url, headers=self._getRequestHeaders())
            statusCode = response.status_code

            if statusCode < 200 or statusCode > 299:
                raise InvalidHTTPResponseException(
                    'Received invalid response during currency rates online refresh',
                    response,
                )

            responseText = response.text
            parsedData = self._parseJsonText(responseText)

            with open(self._ratesFilePath, 'w') as file:
                file.write(responseText)

            self._logger.log(
                f'{Logs.catRateUpdater}Online refresh success, '
                f'cachedAt: {parsedData.cachedAt}, refreshedAt: {parsedData.refreshedAt}',
            )

            self._currencyConverter.refreshUnits(parsedData.currencies)

            return CurrenciesRefreshResult(True, False, parsedData)
        except Exception as e:
            self._logger.log(
                f'{Logs.catRateUpdater}EXCEPTION in currency rates update - online refresh:\n'
                f'{ExceptionHandler.formatExceptionLog(e)}',
            )

            return CurrenciesRefreshResult(False, True)

    def _parseJsonText(self, text: str) -> CurrenciesFileData:
        data = json.loads(text)

        return CurrenciesFileData(
            data['refreshedAt'],
            data['cachedAt'],
            data['currencies'],
        )

    def _updateCheck(self) -> None:
        if self._lastOnlineRefreshAt and (int(time.time()) - self._UPDATE_INTERVAL) < self._lastOnlineRefreshAt:
            return

        threading.Thread(target=self._refreshFromOnline, daemon=True).start()

    def _getRequestHeaders(self) -> dict[str, str]:
        if not hasattr(self, '_requestHeaders'):
            self._requestHeaders = {
                'User-Agent': 'SC:' + json.dumps({
                    'app': self._config.getAppVersion(),
                    'python': platform.python_version(),
                    'os': self._osSwitch.os,
                    'platform': platform.platform(),
                    'name': hashlib.md5(platform.node().encode()).hexdigest(),
                })
            }

        return self._requestHeaders
