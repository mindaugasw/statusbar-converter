# mypy: disable-error-code="type-abstract"
import platform
import sys
import time

from src.Constant.AppConstant import AppConstant
from src.Constant.Logs import Logs
from src.Service.AppLoop import AppLoop
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.Logger import Logger
from src.Service.OSSwitch import OSSwitch
from src.Service.ServiceContainer import ServiceContainer
from src.Service.StatusbarApp import StatusbarApp


def main() -> None:
    services = ServiceContainer(True)

    logger = services[Logger]
    config = services[Configuration]
    osSwitch = services[OSSwitch]
    debug = services[Debug]
    clipboardManager = services[ClipboardManager]

    logger.logRaw(
        f'\n{AppConstant.appName} v{config.getAppVersion()}\n'
        f'Platform: {platform.platform()}\n'
        f'Detected OS: {osSwitch.os}\n'
        f'Python: {sys.version}\n'
        f'Debug: {"enabled" if debug.isDebugEnabled() else "disabled"}\n\n'
    )

    sleepTime = services[ArgumentParser].getSleep()

    if sleepTime is not None:
        logger.log(f'{Logs.catStart}Sleeping for {sleepTime} seconds...')
        time.sleep(sleepTime)
        logger.log(f'{Logs.catStart}Done sleeping, starting the app')

    logger.setDebugEnabled(debug.isDebugEnabled())

    if not clipboardManager.validateSystem():
        logger.log(f'{Logs.catClipboard}Clipboard validate system failed, exiting app')

        return

    services[AutostartManager].setupAutostart()
    clipboardManager.initializeClipboardWatch()
    services[AppLoop].startLoop()
    services[StatusbarApp].createApp()


if __name__ == '__main__':
    main()
