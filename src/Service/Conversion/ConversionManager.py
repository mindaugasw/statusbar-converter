import time
import traceback

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.Service.Configuration import Configuration
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Debug import Debug
from src.Service.EventService import EventService
from src.Service.Logger import Logger


class ConversionManager:
    _converters: list[ConverterInterface]
    _events: EventService
    _logger: Logger
    _debug: Debug

    _clearOnChangeEnabled: bool
    _clearAfterTime: int
    _convertedAt: int | None = None

    def __init__(
        self,
        converters: list[ConverterInterface],
        events: EventService,
        config: Configuration,
        logger: Logger,
        debug: Debug,
    ):
        self._converters = [c for c in converters if c.isEnabled()]
        self._events = events
        self._logger = logger
        self._debug = debug

        self._clearOnChangeEnabled = config.get(ConfigId.ClearOnChange)
        self._clearAfterTime = config.get(ConfigId.ClearAfterTime)

        self._events.subscribeClipboardChanged(self.onClipboardChange)

        if self._clearAfterTime > 0:
            self._events.subscribeAppLoopIteration(self._tryClearAfterTime)

    def onClipboardChange(self, text: str | None) -> None:
        if text is None:
            self._tryClearOnChange()

            return

        for converter in self._converters:
            try:
                success, result = converter.tryConvert(text)
            except Exception as e:
                traceList = traceback.format_exception(e)
                traceString = ''.join(traceList)

                self._logger.log(
                    Logs.catConverter + '%s] CONVERTER EXCEPTION:\nType: %s\nMessage: %s\nTrace: %s' % (
                        converter.getName(),
                        type(e),
                        e,
                        traceString,
                    ),
                )

                continue

            if not success:
                continue

            if self._debug.isDebugEnabled():
                self._logger.log(
                    Logs.catConverter + '%s] Converted to: %s / %s / %s' % (
                        result.converterName,
                        result.iconText,
                        result.originalText,
                        result.convertedText,
                    )
                )

            self._convertedAt = int(time.time())
            self._events.dispatchConverted(result)

            return

        self._tryClearOnChange()

    def dispatchClear(self, reason: str) -> None:
        self._logger.logDebug(Logs.catConvert + ' Statusbar clear: ' + reason)

        self._convertedAt = None
        self._events.dispatchStatusbarClear()

    def _tryClearOnChange(self) -> None:
        if not self._clearOnChangeEnabled:
            return

        if self._convertedAt is None:
            return

        self.dispatchClear('on_change')

    def _tryClearAfterTime(self) -> None:
        if self._convertedAt is None:
            return

        if int(time.time()) - self._convertedAt < self._clearAfterTime:
            return

        self.dispatchClear('after_time ' + str(self._clearAfterTime))
