from AppKit import NSPasteboard, NSStringPboardType, NSArray  # type: ignore[attr-defined]

from src.Service.ClipboardManager import ClipboardManager
from src.Service.EventService import EventService
from src.Service.Logger import Logger


class ClipboardManagerMacOs(ClipboardManager):
    _pasteboard: NSPasteboard

    _changeCount: int

    def __init__(self, events: EventService, logger: Logger):
        super().__init__(events, logger)

        self._changeCount = -1

    def validateSystem(self) -> bool:
        return True

    def initializeClipboardWatch(self) -> None:
        self._pasteboard = NSPasteboard.generalPasteboard()
        self._changeCount = self._pasteboard.changeCount()
        self._events.subscribeAppLoopIteration(self._checkClipboardNew)

    def setClipboardContent(self, content: str) -> None:
        try:
            # From https://stackoverflow.com/a/3555675/4110469
            self._pasteboard.clearContents()
            contentArray = NSArray.arrayWithObject_(content)
            self._pasteboard.writeObjects_(contentArray)
        except Exception as e:
            raise Exception('Could not set clipboard content.\nOriginal exception: ' + str(e))

    def _checkClipboardNew(self) -> None:
        # From https://stackoverflow.com/a/8317794/4110469
        # Apple documentation: https://developer.apple.com/documentation/appkit/nspasteboard

        newChangeCount = self._pasteboard.changeCount()

        if newChangeCount == self._changeCount:
            return

        self._changeCount = newChangeCount
        content = self._pasteboard.stringForType_(NSStringPboardType)

        if content is None:
            # None can be returned when copied content was not string type (e.g. picture, file)
            return

        self._handleChangedClipboard(content)
