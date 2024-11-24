from src.Service.AppLoop import AppLoop
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Debug import Debug
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.TimestampParser import TimestampParser
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
config = Configuration(configFileManager)
argumentParser = ArgumentParser()
debug = Debug(config, argumentParser, logger)
timestampParser = TimestampParser(config, logger)
timestampTextFormatter = TimestampTextFormatter(config)
updateManager = UpdateManager(config, logger)
autostartManager: AutostartManager
clipboardManager: ClipboardManager
statusbarApp: StatusbarApp

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
        config,
        configFileManager,
        autostartManager,
        updateManager,
        logger,
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
        config,
        configFileManager,
        autostartManager,
        updateManager,
        logger,
    )

appLoop = AppLoop(osSwitch)
