from src.Entity.Event import Event

appLoopIteration = Event()

clipboardChanged = Event()
"""Raised when clipboard content changes, but before parsing content.

Content is not yet parsed, so it's not necessarily a valid timestamp.
If content is too long and should not be parsed, event is called with None argument

@param content: New clipboard content
@type content: str | None
"""

timestampChanged = Event()
"""Raised when clipboard content changes, after parsing it and finding a valid timestamp.

@param content
@type content: Timestamp
"""

timestampClear = Event()
"""Raised when statusbar clear was triggered."""

updateCheckCompleted = Event()
"""Raised when check for app updates is completed.

This could be instead directly coupled between UpdateManager <-> StatusbarApp, but then it
causes circular import error, since both modules try to import each other.

@param version version string or None if no new update was found
@type version: str | None
"""
