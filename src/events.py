from src.Entity.Event import Event

appLoopIteration = Event()

clipboardChanged = Event()
"""Raised when clipboard content changes, but before parsing content.

Content is not yet parsed, so it's not necessarily a valid timestamp.

@param content: New clipboard content
"""

# Raised after clipboard change, if a valid timestamp was found.
# Passed a Timestamp object
timestampChanged = Event()
"""Raised when clipboard content changes, after parsing it and finding a valid timestamp.

@param content
@type content: Timestamp
"""

timestampClear = Event()
"""Raised when statusbar clear was triggered."""
