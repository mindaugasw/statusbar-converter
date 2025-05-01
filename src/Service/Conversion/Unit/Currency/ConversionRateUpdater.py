import json
import os.path
import threading
import time

import requests
from typing_extensions import Final

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.DTO.Exception.InvalidHTTPResponseException import InvalidHTTPResponseException
from src.Service.ArgumentParser import ArgumentParser
from src.Service.Configuration import Configuration
from src.Service.Conversion.Unit.Currency.CurrencyConverter import CurrencyConverter
from src.Service.EventService import EventService
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger


class ConversionRateUpdater:
    """
    Terms:
    refreshed_at - time of the actual rates, as returned by the API
    cached_at - when were rates retrieved and cached by my script
    parsed_at - when desktop application parsed data
    """

    _DEFAULT_URL: Final[str] = 'https://storage.googleapis.com/bucket-statusbar-converter-prod/currency_rates.json'
    _CACHED_RATES_MAX_AGE: Final[int] = 3600 * 3  # 3 hours

    _currencyConverter: CurrencyConverter
    _config: Configuration
    _events: EventService
    _logger: Logger

    _url: str
    _isInitialized: bool
    # TODO create a DTO for data? Or maybe completely remove class property?
    _data: dict
    _ratesFilePath: str
    _lastOnlineRefreshAt: int

    def __init__(
        self,
        currencyConverter: CurrencyConverter,
        filesystemHelper: FilesystemHelper,
        argumentParser: ArgumentParser,
        config: Configuration,
        events: EventService,
        logger: Logger,
    ):
        self._currencyConverter = currencyConverter
        self._config = config
        self._events = events
        self._logger = logger

        self._isInitialized = False
        self._ratesFilePath = filesystemHelper.getUserDataDir() + '/currency_rates.json'

        urlOverride = argumentParser.getCurrencyRatesUrl()
        self._url = urlOverride if urlOverride is not None else self._DEFAULT_URL

    def initializeRatesAsync(self) -> None:
        if not self._config.get(ConfigId.Converter_Currency_Enabled):
            return

        threading.Thread(target=self._initializeRates, daemon=True).start()

    def _initializeRates(self) -> None:
        self._logger.log(f'{Logs.catRateUpdater}Initialize - starting currency rates initialization')

        fileResult = self._refreshFromLocalFile()

        self._logger.log(
            f'{Logs.catRateUpdater}Initialize - local refresh {"success" if fileResult["parsedSuccessfully"] else "FAIL"}, '
            f'success: {fileResult["parsedSuccessfully"]}, doOnlineRefresh: {fileResult["shouldDoOnlineRefresh"]}, '
            f'cachedAt: {fileResult["data"]["cachedAt"] if fileResult["parsedSuccessfully"] else "-"}, '
            f'refreshedAt: {fileResult["data"]["refreshedAt"] if fileResult["parsedSuccessfully"] else "-"}',
        )

        if fileResult['parsedSuccessfully']:
            self._data = fileResult['data']

        if fileResult['shouldDoOnlineRefresh']:
            onlineResult = self._refreshFromOnline()

            self._logger.log(
                f'{Logs.catRateUpdater}Initialize - online refresh {"success" if onlineResult["refreshedSuccessfully"] else "FAIL"}, '
                f'success: {onlineResult["refreshedSuccessfully"]}, '
                f'cachedAt: {onlineResult["data"]["cachedAt"] if onlineResult["refreshedSuccessfully"] else "-"}, '
                f'refreshedAt: {onlineResult["data"]["refreshedAt"] if onlineResult["refreshedSuccessfully"] else "-"}',
            )

            if onlineResult['refreshedSuccessfully']:
                self._data = onlineResult['data']

        # TODO class property probably not needed
        if hasattr(self, '_data') and bool(self._data):
            self._isInitialized = True
            self._currencyConverter.refreshUnits(self._data['currencies'])

        # TODO subscribe to loop event

    def _refreshFromLocalFile(self) -> dict:
        result = {
            'parsedSuccessfully': False,
            'shouldDoOnlineRefresh': False,
            'data': {},
        }

        try:
            if not os.path.isfile(self._ratesFilePath):
                result['parsedSuccessfully'] = False
                result['shouldDoOnlineRefresh'] = True
                return result

            with open(self._ratesFilePath, 'r') as file:
                text = file.read()
                parsedData = self._parseJsonText(text)

                if int(time.time()) - parsedData['cachedAt'] > self._CACHED_RATES_MAX_AGE:
                    result['shouldDoOnlineRefresh'] = True
                else:
                    result['shouldDoOnlineRefresh'] = False
                    self._lastOnlineRefreshAt = parsedData['cachedAt']

                result['parsedSuccessfully'] = True
                result['data'] = parsedData

                return result
        except Exception as e:
            self._logger.log(
                f'{Logs.catRateUpdater}EXCEPTION in currency rates update - local file parsing:\n'
                f'{ExceptionHandler.formatExceptionLog(e)}',
            )

            result['parsedSuccessfully'] = False
            result['shouldDoOnlineRefresh'] = True
            result['data'] = {}

            return result

    def _refreshFromOnline(self) -> dict:
        self._lastOnlineRefreshAt = int(time.time())

        result = {
            'refreshedSuccessfully': False,
            'data': {},
        }

        try:
            response = requests.get(self._url, {'ts': int(time.time())})
            statusCode = response.status_code

            if statusCode < 200 or statusCode > 299:
                raise InvalidHTTPResponseException('Received invalid response during currency rates online refresh', response)

            responseText = response.text
            parsedData = self._parseJsonText(responseText)

            with open(self._ratesFilePath, 'w') as file:
                file.write(responseText)

            result['refreshedSuccessfully'] = True
            result['data'] = parsedData

            return result
        except Exception as e:
            self._logger.log(
                f'{Logs.catRateUpdater}EXCEPTION in currency rates update - online refresh:\n'
                f'{ExceptionHandler.formatExceptionLog(e)}',
            )

            result['refreshedSuccessfully'] = False

            return result

    def _parseJsonText(self, text: str) -> dict:
        data = json.loads(text)

        # TODO is this method needed? Maybe convert dict to DTO here? Or else delete method

        return data
