from src.Service.ArgumentParser import ArgumentParser
from src.Service.OSSwitch import OSSwitch
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Configuration import Configuration
from src.Service.TimestampParser import TimestampParser
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Debug import Debug
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.StatusbarApp import StatusbarApp
from src.Service.AppLoop import AppLoop
from src.Service.UpdateManager import UpdateManager

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
argumentParser = ArgumentParser()
debug = Debug(config, argumentParser)
timestampParser = TimestampParser(config, debug)
timestampTextFormatter = TimestampTextFormatter(config)
updateManager = UpdateManager(config, debug)
autostartManager: AutostartManager
clipboardManager: ClipboardManager
statusbarApp: StatusbarApp

if osSwitch.isMacOS():
    from src.Service.AutostartManagerMacOS import AutostartManagerMacOS
    from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
    from src.Service.StatusbarAppMacOs import StatusbarAppMacOs

    autostartManager = AutostartManagerMacOS(config, debug)
    clipboardManager = ClipboardManagerMacOs(debug)
    statusbarApp = StatusbarAppMacOs(
        osSwitch,
        timestampTextFormatter,
        clipboardManager,
        config,
        configFileManager,
        autostartManager,
        updateManager,
        debug,
    )
else:
    from src.Service.AutostartManagerLinux import AutostartManagerLinux
    from src.Service.ClipboardManagerLinux import ClipboardManagerLinux
    from src.Service.StatusbarAppLinux import StatusbarAppLinux

    autostartManager = AutostartManagerLinux(config, debug)
    clipboardManager = ClipboardManagerLinux(debug)
    statusbarApp = StatusbarAppLinux(
        osSwitch,
        timestampTextFormatter,
        clipboardManager,
        config,
        configFileManager,
        autostartManager,
        updateManager,
        debug,
    )

appLoop = AppLoop(osSwitch)
