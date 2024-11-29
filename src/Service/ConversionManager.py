import time

import src.events as events
from src.Constant.Logs import Logs
from src.Service.Configuration import Configuration
from src.Service.Converter.ConverterInterface import ConverterInterface
from src.Service.Debug import Debug
from src.Service.Logger import Logger


class ConversionManager:
    _converters: list[ConverterInterface]
    _logger: Logger
    _debug: Debug

    _clearOnChangeEnabled: bool
    _clearAfterTime: int
    _convertedAt: int | None = None

    def __init__(self, converters: list[ConverterInterface], config: Configuration, logger: Logger, debug: Debug):
        self._converters = converters
        self._logger = logger
        self._debug = debug

        self._clearOnChangeEnabled = config.get(config.CLEAR_ON_CHANGE)
        self._clearAfterTime = config.get(config.CLEAR_AFTER_TIME)

        events.clipboardChanged.append(self.onClipboardChange)

        if self._clearAfterTime > 0:
            events.appLoopIteration.append(self._tryClearAfterTime)

    def onClipboardChange(self, content: str | None) -> None:
        if content is None:
            self._tryClearOnChange()

            return

        for converter in self._converters:
            success, result = converter.tryConvert(content)

            if not success:
                continue

            if self._debug.isDebugEnabled():
                self._logger.log(
                    Logs.catConverter + '%s] Converted to: %s / %s / %s' % (
                        converter.getConverterName(),
                        result.iconText,
                        result.originalText,
                        result.convertedText,
                    )
                )

            self._convertedAt = int(time.time())
            events.converted(result)

            return

        self._tryClearOnChange()

    def dispatchClear(self, reason: str) -> None:
        self._logger.logDebug(Logs.catConvert + ' Statusbar clear: ' + reason)

        self._convertedAt = None
        events.statusbarClear()

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
