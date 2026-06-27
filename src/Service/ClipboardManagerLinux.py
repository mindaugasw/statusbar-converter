import gi

from src.Constant.ConfigId import ConfigId
from src.Constant.Logs import Logs
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Configuration import Configuration
from src.Service.EventService import EventService
from src.Service.Logger import Logger

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gtk  # type: ignore[attr-defined]  # noqa: E402


class ClipboardManagerLinux(ClipboardManager):
    """
    On Linux there are 2 "selections" that can be monitored:
    - PRIMARY - when text is highlighted. Also acts as mouse middle-click paste.
    - CLIPBOARD - when text is explicitly copied (e.g. with Ctrl+C). This value can be pasted with Ctrl+V.
    """

    _config: Configuration

    _clipboardSelection: Gtk.Clipboard

    def __init__(
        self,
        events: EventService,
        logger: Logger,
        config: Configuration,
    ):
        super().__init__(events, logger)

        self._config = config

    def validateSystem(self) -> bool:
        # init_check() performs GTK initialization: opens a connection to the default display
        # (X server, or Wayland via GDK), sets up the GTK type system. On failure returns False,
        # instead of aborting like init().
        success, _ = Gtk.init_check()

        if not success:
            self._logger.log(Logs.catClipboard + 'No display available, cannot access clipboard')

        return success

    def initializeClipboardWatch(self) -> None:
        # CLIPBOARD (explicit Ctrl+C) is always monitored.
        # PRIMARY (text highlighting) is monitored based on config.
        # The watcher is driven by GTK's `owner-change` signal on the main loop,
        # started by `Gtk.main()` in StatusbarAppLinux.
        self._clipboardSelection = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self._clipboardSelection.connect('owner-change', self._onSelectionChange)

        if self._config.get(ConfigId.General_ConvertOnHighlight):
            Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).connect('owner-change', self._onSelectionChange)

    def setClipboardContent(self, content: str) -> None:
        # Write only to CLIPBOARD (pastes with Ctrl+V). Skipping PRIMARY to trigger only one
        # `owner-change` event, so the value is parsed by the app itself only once and icon
        # flashes only once
        self._clipboardSelection.set_text(content, -1)

    def _onSelectionChange(self, clipboard: Gtk.Clipboard, _event: Gdk.EventOwnerChange) -> None:
        text = clipboard.wait_for_text()

        # None when the selection holds non-text content (e.g. an image or file)
        if text is not None:
            self._handleChangedClipboard(text)
