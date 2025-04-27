from typing import Callable

from typing_extensions import Final

from src.DTO.ConvertResult import ConvertResult
from src.DTO.Event import Event
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Type.Types import DialogButtonsDict


class EventService:
    _ID_APP_LOOP_ITERATION: Final[str] = 'app_loop_iteration'
    _ID_CLIPBOARD_CHANGED: Final[str] = 'clipboard_changed'
    _ID_CONVERTED: Final[str] = 'converted'
    _ID_STATUSBAR_CLEAR: Final[str] = 'statusbar_clear'
    _ID_UPDATE_CHECK_COMPLETED: Final[str] = 'update_check_completed'
    _ID_DELAYED_CONVERTER_INITIALIZED: Final[str] = 'delayed_converter_initialized'

    _events: dict[str, Event]

    def __init__(self):
        self._events = {}

    def subscribeAppLoopIteration(self, callback: Callable[[], None]) -> None:
        self._subscribe(self._ID_APP_LOOP_ITERATION, callback)

    def dispatchAppLoopIteration(self) -> None:
        self._dispatch(self._ID_APP_LOOP_ITERATION)

    def subscribeClipboardChanged(self, callback: Callable[[str | None], None]) -> None:
        """Raised when clipboard content changes, but before parsing it.

        Content has whitespace trimmed.
        If content is too long and should not be parsed, event is called with None argument.
        """
        self._subscribe(self._ID_CLIPBOARD_CHANGED, callback)

    def dispatchClipboardChanged(self, content: str | None) -> None:
        self._dispatch(self._ID_CLIPBOARD_CHANGED, content)

    def subscribeConverted(self, callback: Callable[[ConvertResult], None]) -> None:
        """Raised when one of the converters successfully converted newly changed clipboard content."""
        self._subscribe(self._ID_CONVERTED, callback)

    def dispatchConverted(self, result: ConvertResult) -> None:
        self._dispatch(self._ID_CONVERTED, result)

    def subscribeStatusbarClear(self, callback: Callable[[], None]) -> None:
        """Raised when statusbar clear was triggered."""
        self._subscribe(self._ID_STATUSBAR_CLEAR, callback)

    def dispatchStatusbarClear(self) -> None:
        self._dispatch(self._ID_STATUSBAR_CLEAR)

    def subscribeUpdateCheckCompleted(self, callback: Callable[[str, DialogButtonsDict], None]) -> None:
        """Raised when check for app updates is completed.

        This could be instead directly coupled between UpdateManager <-> StatusbarApp, but then it
        causes circular import error, since both modules try to import each other.

        Params:
        - text: str, text to show in a dialog
        - buttons: DialogButtonsDict, buttons to show and their callbacks
        """
        self._subscribe(self._ID_UPDATE_CHECK_COMPLETED, callback)

    def dispatchUpdateCheckCompleted(self, text: str, buttons: DialogButtonsDict) -> None:
        self._dispatch(self._ID_UPDATE_CHECK_COMPLETED, text, buttons)

    def subscribeDelayedConverterInitialized(self, callback: Callable[[UnitConverterInterface], None]) -> None:
        self._subscribe(self._ID_DELAYED_CONVERTER_INITIALIZED, callback)

    def dispatchDelayedConverterInitialized(self, converter: UnitConverterInterface) -> None:
        self._dispatch(self._ID_DELAYED_CONVERTER_INITIALIZED, converter)

    def _subscribe(self, _eventId: str, callback: Callable) -> None:
        if _eventId not in self._events:
            self._events[_eventId] = Event()

        self._events[_eventId].append(callback)

    def _dispatch(self, _eventId: str, *args) -> None:
        self._events[_eventId](*args)
