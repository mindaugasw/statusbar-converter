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
    _config: Configuration

    _monitoredSelection: Gtk.Clipboard  # TODO rename? _monitoredClipboard

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
        # The watch is driven by GTK's `owner-change` signal on the main loop (started later by
        # StatusbarAppLinux.createApp() -> Gtk.main()), so no separate thread is needed.
        self._monitoredSelection = Gtk.Clipboard.get(self._getMonitoredSelectionType())
        self._monitoredSelection.connect('owner-change', self._onSelectionChange)  # TODO monitor both clipboards - so that it would re-parse on Ctrl+C. Value not necessarily has to be selected, can be copied programatically

    def setClipboardContent(self, content: str) -> None:
        # Write to both selections: CLIPBOARD so the value pastes with Ctrl+V, and PRIMARY so it
        # pastes with middle-click and so the monitor (when set to PRIMARY) fires `owner-change`,
        # giving visual feedback that the copied value was detected and parsed.
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(content, -1)  # TODO cache reference in class variable
        Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).set_text(content, -1)

    def _onSelectionChange(self, _clipboard: Gtk.Clipboard, _event: Gdk.EventOwnerChange) -> None:
        text = self._monitoredSelection.wait_for_text()

        # None when the clipboard holds non-text content (e.g. an image or file)
        if text is not None:
            self._handleChangedClipboard(text)

    def _getMonitoredSelectionType(self) -> Gdk.Atom:
        # convert_on_highlight: True -> PRIMARY (react to text selection/highlight),
        # False -> CLIPBOARD (react to an explicit Ctrl+C copy).
        if self._config.get(ConfigId.General_ConvertOnHighlight):
            return Gdk.SELECTION_PRIMARY

        return Gdk.SELECTION_CLIPBOARD
