import platform
import time

import src.services as services
import sys
from src.Service.StatusbarApp import StatusbarApp


def main():
    print(
        f'\n{StatusbarApp.APP_NAME} v{services.config.getAppVersion()}\n'
        f'Platform: {platform.platform()}\n'
        f'Detected OS: {services.osSwitch.os}\n'
        f'Python: {sys.version}\n'
        f'Debug: {"enabled" if services.debug.isDebugEnabled() else "disabled"}\n'
    )

    sleepTime = services.argumentParser.getSleep()

    if sleepTime is not None:
        print(f'Sleeping for {sleepTime} seconds...')
        time.sleep(services.argumentParser.getSleep())
        print(f'Done sleeping, starting the app')

    services.autostartManager.setAppName(StatusbarApp.APP_NAME)
    services.autostartManager.firstTimeSetup()
    services.clipboardManager.initializeClipboardWatch()
    services.appLoop.startLoop()
    services.statusbarApp.createApp()


main()
