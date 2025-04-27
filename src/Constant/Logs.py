from typing import Final


class Logs:
    # cat prefix for category
    catAutostart: Final[str] = '[Autostart] '
    catClipboard: Final[str] = '[Clipboard] '
    catConfig: Final[str] = '[Config] '
    catConvert: Final[str] = '[Convert] '
    catConverter: Final[str] = '[Convert.'
    catMenuApp: Final[str] = '[Menu app] '
    catModal: Final[str] = '[Modal] '
    catModalSub: Final[str] = '[Modal.'
    catRateUpdater: Final[str] = '[Rate updater] '
    catUpdateCheck: Final[str] = '[Update check] '
    catStart: Final[str] = '[Start] '
    catSettings: Final[str] = catModalSub + 'Settings] '

    changingIconTextTo: Final[str] = catMenuApp + 'Changing icon text to: %s'
