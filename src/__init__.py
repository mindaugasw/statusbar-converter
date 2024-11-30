import platform
import sys
import time

import src.services as services
from src.Service.Logger import Logger
from src.Service.StatusbarApp import StatusbarApp


def main() -> None:
    services.logger.logRaw(
        f'\n{StatusbarApp.APP_NAME} v{services.config.getAppVersion()}\n'
        f'Platform: {platform.platform()}\n'
        f'Detected OS: {services.osSwitch.os}\n'
        f'Python: {sys.version}\n'
        f'Debug: {"enabled" if services.debug.isDebugEnabled() else "disabled"}\n\n'
    )

    sleepTime = services.argumentParser.getSleep()

    if sleepTime is not None:
        services.logger.log(f'[Start] Sleeping for {sleepTime} seconds...')
        time.sleep(services.argumentParser.getSleep())
        services.logger.log(f'[Start] Done sleeping, starting the app')

    services.logger.setDebugEnabled(services.debug.isDebugEnabled())
    services.autostartManager.setAppName(StatusbarApp.APP_NAME)
    services.autostartManager.firstTimeSetup()
    services.clipboardManager.initializeClipboardWatch()
    services.appLoop.startLoop()
    services.statusbarApp.createApp()


main()
