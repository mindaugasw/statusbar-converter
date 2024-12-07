from src.Constant.ModalId import ModalId
from src.Service.AppLoop import AppLoop
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.ConversionManager import ConversionManager
from src.Service.Converter.TimestampConverter import TimestampConverter
from src.Service.Debug import Debug
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.AboutBuilder import AboutBuilder
from src.Service.ModalWindow.DemoBuilder import DemoBuilder
from src.Service.ModalWindow.DialogBuilder import DialogBuilder
from src.Service.ModalWindow.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Service.ModalWindow.ModalWindowManager import ModalWindowManager
from src.Service.ModalWindow.SettingsBuilder import SettingsBuilder
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.UpdateManager import UpdateManager

osSwitch = OSSwitch()
filesystemHelper: FilesystemHelper

if osSwitch.isMacOS():
    from src.Service.FilesystemHelperMacOs import FilesystemHelperMacOs
    filesystemHelper = FilesystemHelperMacOs()
else:
    from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
    filesystemHelper = FilesystemHelperLinux()

logger = Logger(filesystemHelper)

logger.logRaw(filesystemHelper.getInitializationLogs())
ExceptionHandler.initialize()

configFileManager = ConfigFileManager(filesystemHelper, logger)
config = Configuration(configFileManager, logger)
argumentParser = ArgumentParser()
debug = Debug(config, argumentParser)
timestampTextFormatter = TimestampTextFormatter(config)
updateManager = UpdateManager(filesystemHelper, config, logger, debug)
autostartManager: AutostartManager
clipboardManager: ClipboardManager
statusbarApp: StatusbarApp
guiBuilders: dict[str, ModalWindowBuilderInterface] = {
    ModalId.demo: DemoBuilder(),
    ModalId.settings: SettingsBuilder(),
    ModalId.about: AboutBuilder(config),
    ModalId.dialog: DialogBuilder(),
}
modalWindowManager = ModalWindowManager(guiBuilders, osSwitch, logger)

converters = [
    TimestampConverter(timestampTextFormatter, config, logger),
]

conversionManager = ConversionManager(converters, config, logger, debug)

if osSwitch.isMacOS():
    from src.Service.AutostartManagerMacOS import AutostartManagerMacOS
    from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
    from src.Service.StatusbarAppMacOs import StatusbarAppMacOs

    autostartManager = AutostartManagerMacOS(config, filesystemHelper, logger)
    clipboardManager = ClipboardManagerMacOs(logger)
    statusbarApp = StatusbarAppMacOs(
        osSwitch,
        timestampTextFormatter,
        clipboardManager,
        conversionManager,
        config,
        configFileManager,
        autostartManager,
        updateManager,
        modalWindowManager,
        logger,
        debug,
    )
else:
    from src.Service.AutostartManagerLinux import AutostartManagerLinux
    from src.Service.ClipboardManagerLinux import ClipboardManagerLinux
    from src.Service.StatusbarAppLinux import StatusbarAppLinux

    autostartManager = AutostartManagerLinux(config, filesystemHelper, logger)
    clipboardManager = ClipboardManagerLinux(logger)
    statusbarApp = StatusbarAppLinux(
        osSwitch,
        timestampTextFormatter,
        clipboardManager,
        conversionManager,
        config,
        configFileManager,
        autostartManager,
        updateManager,
        modalWindowManager,
        logger,
        debug,
    )

appLoop = AppLoop(osSwitch)
