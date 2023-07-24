import pasteboard
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Debug import Debug
import src.events as events


class ClipboardManagerMacOs(ClipboardManager):
    _pb: pasteboard.Pasteboard
    _firstIteration = True

    def __init__(self, debug: Debug):
        super().__init__(debug)
        self._pb = pasteboard.Pasteboard()

    def initializeClipboardWatch(self) -> None:
        events.appLoopIteration.append(self._checkClipboard)

    def _checkClipboard(self) -> None:
        content = self._pb.get_contents(type=pasteboard.String, diff=True)

        # On the first call Pasteboard will return content copied before
        # opening the app, which we should not parse
        if self._firstIteration:
            self._firstIteration = False

            return

        # If content did not change between 2 polls, pb.get_contents() will return None
        if content is None:
            return

        # Avoid parsing huge texts to not impact performance
        if len(content) > ClipboardManagerMacOs.MAX_CONTENT_LENGTH:
            self._debug.log('Too long clipboard content, skipping')

            return

        trimmed = content.strip()

        if len(trimmed) > ClipboardManagerMacOs.MAX_CONTENT_LENGTH_TRIMMED:
            self._debug.log('Too long clipboard content after trimming, skipping')

            return

        events.clipboardChanged(content.strip())

    def setClipboardContent(self, content: str) -> None:
        try:
            self._pb.set_contents(content)
        except Exception as e:
            raise Exception('Could not set clipboard content.\nOriginal exception: ' + str(e))
