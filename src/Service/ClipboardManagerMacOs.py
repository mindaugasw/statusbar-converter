import pasteboard
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Debug import Debug
import src.events as events


class ClipboardManagerMacOs(ClipboardManager):
    MAX_CONTENT_LENGTH = 1000

    _pb: pasteboard.Pasteboard
    _debug: Debug
    _firstIteration = True

    def __init__(self, debug: Debug):
        self._debug = debug
        self._pb = pasteboard.Pasteboard()

        events.appLoopIteration.append(self._checkClipboard)

    def _checkClipboard(self) -> None:
        content = self._pb.get_contents(type=pasteboard.String, diff=True)

        # On the first call Pasteboard will return content copied before
        # opening the app, which is we should not parse
        if self._firstIteration:
            self._firstIteration = False

            return

        # If content did not change between 2 polls, pb.get_contents() will
        # return None
        if content is None:
            return

        if len(content) > self.MAX_CONTENT_LENGTH:
            # Avoid parsing huge texts to not impact performance
            return

        events.clipboardChanged(content.strip())

    def setClipboardContent(self, content: str) -> None:
        try:
            self._pb.set_contents(content)
        except Exception as e:
            # TODO create a custom exception class that allows passing previous exception
            raise Exception('Could not set clipboard content.\nOriginal exception: ' + str(e))
