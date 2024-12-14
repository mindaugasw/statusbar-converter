from typing import Callable

from src.DTO.ConvertResult import ConvertResult
from src.DTO.Event import Event


class EventService:
    # TODO add event blocking: block all events before showing UI window, and unblock afterwards.
    #  To not crash application with incoming events while UI thread is blocked
    #  EventService.blockEvents()
    #  EventService.unblockEvents()

    _idAppLoopIteration = 'app_loop_iteration'
    _idClipboardChanged = 'clipboard_changed'
    _idConverted = 'converted'
    _idStatusbarClear = 'statusbar_clear'
    _idUpdateCheckCompleted = 'update_check_completed'

    _events: dict[str, Event] = {}

    def subscribeAppLoopIteration(self, callback: Callable[[], None]) -> None:
        self._subscribe(self._idAppLoopIteration, callback)

    def dispatchAppLoopIteration(self) -> None:
        self._dispatch(self._idAppLoopIteration)

    def subscribeClipboardChanged(self, callback: Callable[[str | None], None]) -> None:
        """Raised when clipboard content changes, but before parsing it.

        Content has whitespace trimmed.
        If content is too long and should not be parsed, event is called with None argument.
        """
        self._subscribe(self._idClipboardChanged, callback)

    def dispatchClipboardChanged(self, content: str | None) -> None:
        self._dispatch(self._idClipboardChanged, content)

    def subscribeConverted(self, callback: Callable[[ConvertResult], None]) -> None:
        """Raised when one of the converters successfully converted newly changed clipboard content."""
        self._subscribe(self._idConverted, callback)

    def dispatchConverted(self, result: ConvertResult) -> None:
        self._dispatch(self._idConverted, result)

    def subscribeStatusbarClear(self, callback: Callable[[], None]) -> None:
        """Raised when statusbar clear was triggered."""
        self._subscribe(self._idStatusbarClear, callback)

    def dispatchStatusbarClear(self) -> None:
        self._dispatch(self._idStatusbarClear)

    def subscribeUpdateCheckCompleted(self, callback: Callable[[str, dict[str, Callable | None]], None]) -> None:
        """Raised when check for app updates is completed.

        This could be instead directly coupled between UpdateManager <-> StatusbarApp, but then it
        causes circular import error, since both modules try to import each other.

        Params:
        - text: str, text to show in a dialog
        - buttons: dict[str, Callable | None], buttons to show and their callbacks
        """
        self._subscribe(self._idUpdateCheckCompleted, callback)

    def dispatchUpdateCheckCompleted(self, text: str, buttons: dict[str, Callable | None]) -> None:
        self._dispatch(self._idUpdateCheckCompleted, text, buttons)

    def _subscribe(self, _eventId: str, callback: Callable) -> None:
        if _eventId not in self._events:
            self._events[_eventId] = Event()

        self._events[_eventId].append(callback)

    def _dispatch(self, _eventId: str, *args) -> None:
        self._events[_eventId](*args)
