import platform
import src.services as services
import sys
from src.Service.StatusbarApp import StatusbarApp


def main():
    if services.osSwitch.isMacOS():
        _hideMacOSDockIcon()

    # TODO print app version as well
    print(
        f'\n{StatusbarApp.APP_NAME}\n'
        f'Platform: {platform.platform()}\n'
        f'Detected OS: {services.osSwitch.os}\n'
        f'Python: {sys.version}\n'
    )

    services.appLoop.startLoop()
    services.statusbarApp.createApp()


def _hideMacOSDockIcon():
    import AppKit
    info = AppKit.NSBundle.mainBundle().infoDictionary()
    info['LSBackgroundOnly'] = '1'


main()
