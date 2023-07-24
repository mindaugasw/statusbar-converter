from src.Service.OSSwitch import OSSwitch
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Configuration import Configuration
from src.Service.TimestampParser import TimestampParser
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Debug import Debug
from src.Service.ClipboardManager import ClipboardManager
from src.Service.StatusbarApp import StatusbarApp
from src.Service.AppLoop import AppLoop

osSwitch = OSSwitch()
filesystemHelper: FilesystemHelper

if osSwitch.isMacOS():
    from src.Service.FilesystemHelperMacOs import FilesystemHelperMacOs
    filesystemHelper = FilesystemHelperMacOs()
else:
    from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
    filesystemHelper = FilesystemHelperLinux()

configFileManager = ConfigFileManager(filesystemHelper)
config = Configuration(configFileManager)
debug = Debug(config)
timestampParser = TimestampParser(config, debug)
timestampTextFormatter = TimestampTextFormatter(config)
clipboardManager: ClipboardManager
statusbarApp: StatusbarApp

if osSwitch.isMacOS():
    from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
    from src.Service.StatusbarAppMacOs import StatusbarAppMacOs

    clipboardManager = ClipboardManagerMacOs(debug)
    statusbarApp = StatusbarAppMacOs(
        timestampTextFormatter,
        clipboardManager,
        timestampParser,
        config,
        configFileManager,
        debug,
    )
else:
    from src.Service.ClipboardManagerLinux import ClipboardManagerLinux
    from src.Service.StatusbarAppLinux import StatusbarAppLinux

    clipboardManager = ClipboardManagerLinux()
    statusbarApp = StatusbarAppLinux()

appLoop = AppLoop(clipboardManager)
