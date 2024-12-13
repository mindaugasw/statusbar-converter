from src.DTO.Event import Event

# TODO refactor into a service
# As a bonus, it could allow easily blocking all events, e.g. before showing UI window, and unblocking afterwards. To not crash application with incoming events while UI is blocked
# EventDispatcher.blockEvents()
# EventDispatcher.unblockEvents()
appLoopIteration = Event()

clipboardChanged = Event()
"""Raised when clipboard content changes, but before parsing content.

Content has whitespace trimmed.
If content is too long and should not be parsed, event is called with None argument.

@param content: New clipboard content
@type content: str | None
"""

converted = Event()
"""Raised when one of the converters successfully converted newly changed clipboard content.

@param result
@type result: ConvertResult
"""

statusbarClear = Event()
"""Raised when statusbar clear was triggered."""

updateCheckCompleted = Event()
"""Raised when check for app updates is completed.

This could be instead directly coupled between UpdateManager <-> StatusbarApp, but then it
causes circular import error, since both modules try to import each other.

@param text text to show in a dialog
@type text: str
@param buttons buttons to show and their callbacks
@type buttons: dict[str, Callable | None]
"""
