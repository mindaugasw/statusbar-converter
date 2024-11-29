from src.DTO.Event import Event

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

@param version version string or None if no new update was found
@type version: str | None
"""
