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
from src.Service.Conversion.Unit.Currency.ConversionRateUpdater import ConversionRateUpdater
from src.Service.Debug import Debug
from src.Service.DependencyManager import DependencyManager
from src.Service.DependencyOverrides import DependencyOverrides
from src.Service.Logger import Logger
from src.Service.OSSwitch import OSSwitch
from src.Service.ServiceBuilder import ServiceBuilder
from src.Service.StatusbarApp import StatusbarApp


def main() -> None:
    services = ServiceBuilder().initializeServices()

    logger = services[Logger]
    config = services[Configuration]
    osSwitch = services[OSSwitch]
    debug = services[Debug]
    clipboardManager = services[ClipboardManager]

    logger.logRaw(
        f'\n{AppConstant.APP_NAME} v{config.getAppVersion()}\n'
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
    services[ConversionRateUpdater].initializeRatesAsync()
    services[AppLoop].startLoop()
    services[StatusbarApp].createApp()


def main_v2() -> None:
    osSwitch = OSSwitch()
    depOverrides = DependencyOverrides(osSwitch)
    deps = DependencyManager(depOverrides.getServiceOverrides(), depOverrides.getArgumentOverrides())

    logger = deps[Logger]
    config = deps[Configuration]
    debug = deps[Debug]
    clipboardManager = deps[ClipboardManager]

    logger.logRaw(
        f'\n{AppConstant.APP_NAME} v{config.getAppVersion()}\n'
        f'Platform: {platform.platform()}\n'
        f'Detected OS: {osSwitch.os}\n'
        f'Python: {sys.version}\n'
        f'Debug: {"enabled" if debug.isDebugEnabled() else "disabled"}\n\n'
    )

    sleepTime = deps[ArgumentParser].getSleep()

    if sleepTime is not None:
        logger.log(f'{Logs.catStart}Sleeping for {sleepTime} seconds...')
        time.sleep(sleepTime)
        logger.log(f'{Logs.catStart}Done sleeping, starting the app')

    logger.setDebugEnabled(debug.isDebugEnabled())

    if not clipboardManager.validateSystem():
        logger.log(f'{Logs.catClipboard}Clipboard validate system failed, exiting app')

        return

    # TODO next: step-debug from here
    # Upd: nahh, nvm, dynamic autowiring is becoming too complex here and will be absolutely unmaintainable on init bugs. Just stash it in a separate branch and revert everything
    deps[AutostartManager].setupAutostart()
    clipboardManager.initializeClipboardWatch()
    deps[ConversionRateUpdater].initializeRatesAsync()
    deps[AppLoop].startLoop()
    deps[StatusbarApp].createApp()


if __name__ == '__main__':
    # main()
    main_v2()
