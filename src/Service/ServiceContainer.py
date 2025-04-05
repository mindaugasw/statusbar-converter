from typing import TypeVar

from src.Constant.ModalId import ModalId
from src.Service.AppLoop import AppLoop
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Conversion.ConversionManager import ConversionManager
from src.Service.Conversion.Converter.ConverterInterface import ConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.DistanceConverter import DistanceConverter
from src.Service.Conversion.Converter.SimpleUnit.SimpleConverterInterface import SimpleConverterInterface
from src.Service.Conversion.Converter.SimpleUnit.SimpleUnitConverter import SimpleUnitConverter
from src.Service.Conversion.Converter.SimpleUnit.TemperatureConverter import TemperatureConverter
from src.Service.Conversion.Converter.SimpleUnit.VolumeConverter import VolumeConverter
from src.Service.Conversion.Converter.SimpleUnit.WeightConverter import WeightConverter
from src.Service.Conversion.Converter.Timestamp.TimestampConverter import TimestampConverter
from src.Service.Conversion.Converter.Timestamp.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Conversion.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.UnitParser import UnitParser
from src.Service.Conversion.UnitToConverterMap import UnitToConverterMap
from src.Service.Debug import Debug
from src.Service.EventService import EventService
from src.Service.ExceptionHandler import ExceptionHandler
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.ModalWindowManager import ModalWindowManager
from src.Service.ModalWindow.Modals.AboutBuilder import AboutBuilder
from src.Service.ModalWindow.Modals.CustomizedDialogBuilder import CustomizedDialogBuilder
from src.Service.ModalWindow.Modals.DemoBuilder import DemoBuilder
from src.Service.ModalWindow.Modals.MissingXselBuilder import DialogMissingXselBuilder
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Service.ModalWindow.Modals.SettingsBuilder import SettingsBuilder
from src.Service.OSSwitch import OSSwitch
from src.Service.StatusbarApp import StatusbarApp
from src.Service.UpdateManager import UpdateManager


class ServiceContainer:
    T = TypeVar('T')

    _services: dict[type, object]

    def __init__(self, initialize: bool):
        _: dict[type, object] = {}

        # Core services
        _[OSSwitch] = osSwitch = OSSwitch()
        _[FilesystemHelper] = filesystemHelper = self._getFilesystemHelper(osSwitch)
        _[Logger] = logger = Logger(filesystemHelper)

        if initialize:
            logger.logRaw(filesystemHelper.getInitializationLogs())
            ExceptionHandler.initialize()

        _[ConfigFileManager] = configFileManager = ConfigFileManager(filesystemHelper, logger)
        _[Configuration] = config = Configuration(configFileManager, logger)
        _[ArgumentParser] = argumentParser = ArgumentParser()
        _[Debug] = debug = Debug(config, argumentParser)
        _[EventService] = events = EventService()

        # Conversion services
        _[TimestampTextFormatter] = timestampTextFormatter = TimestampTextFormatter(config)
        _[ThousandsDetector] = thousandsDetector = ThousandsDetector()
        _[DistanceConverter] = distanceConverter = DistanceConverter(config)
        _[VolumeConverter] = volumeConverter = VolumeConverter(config)
        _[WeightConverter] = weightConverter = WeightConverter(config)
        _[TemperatureConverter] = temperatureConverter = TemperatureConverter(config)
        _[list[SimpleConverterInterface]] = simpleConverters = [
            distanceConverter,
            volumeConverter,
            weightConverter,
            temperatureConverter,
        ]

        _[UnitToConverterMap] = unitToConverterMap = UnitToConverterMap(simpleConverters)
        _[UnitParser] = unitParser = UnitParser(unitToConverterMap, thousandsDetector)

        _[list[ConverterInterface]] = converters = [
            TimestampConverter(timestampTextFormatter, config, logger),
            SimpleUnitConverter(unitParser, unitToConverterMap)
        ]
        _[ConversionManager] = conversionManager = ConversionManager(converters, events, config, logger, debug)

        # GUI services
        _[list[ModalWindowBuilderInterface]] = modalWindowBuilders = self._getModalWindowBuilders(config, configFileManager, filesystemHelper, logger)
        _[ModalWindowManager] = modalWindowManager = ModalWindowManager(modalWindowBuilders, osSwitch, logger)

        # App services
        _[UpdateManager] = updateManager = UpdateManager(filesystemHelper, events, config, logger, debug)
        _[AutostartManager] = autostartManager = self._getAutostartManager(osSwitch, filesystemHelper, config, argumentParser, logger)
        _[ClipboardManager] = clipboardManager = self._getClipboardManager(osSwitch, events, logger, modalWindowManager)
        _[StatusbarApp] = statusbarApp = self._getStatusbarApp(osSwitch, timestampTextFormatter, clipboardManager, conversionManager, events, config, configFileManager, autostartManager, updateManager, modalWindowManager, logger, debug)
        _[AppLoop] = appLoop = AppLoop(osSwitch, events)

        self._services = _

    def __getitem__(self, item: type[T]) -> T:
        if item not in self._services:
            raise Exception(f'Service with id "{item}" not found in the container')

        return self._services[item]  # type: ignore[return-value]

    def _getFilesystemHelper(self, osSwitch: OSSwitch) -> FilesystemHelper:
        if osSwitch.isMacOS():
            from src.Service.FilesystemHelperMacOs import FilesystemHelperMacOs
            return FilesystemHelperMacOs()
        else:
            from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
            return FilesystemHelperLinux()

    def _getModalWindowBuilders(
        self,
        config: Configuration,
        configFileManager: ConfigFileManager,
        filesystemHelper: FilesystemHelper,
        logger: Logger,
    ) -> dict[str, ModalWindowBuilderInterface]:
        customizedDialogBuilder = CustomizedDialogBuilder()

        return {
            ModalId.DEMO: DemoBuilder(),
            ModalId.SETTINGS: SettingsBuilder(config, configFileManager, filesystemHelper, logger),
            ModalId.ABOUT: AboutBuilder(config),
            ModalId.CUSTOMIZED_DIALOG: customizedDialogBuilder,
            ModalId.MISSING_XSEL: DialogMissingXselBuilder(customizedDialogBuilder),
        }

    def _getAutostartManager(
        self,
        osSwitch: OSSwitch,
        filesystemHelper: FilesystemHelper,
        config: Configuration,
        argParser: ArgumentParser,
        logger: Logger,
    ) -> AutostartManager:
        if osSwitch.isMacOS():
            from src.Service.AutostartManagerMacOS import AutostartManagerMacOS
            return AutostartManagerMacOS(filesystemHelper, config, argParser, logger)
        else:
            from src.Service.AutostartManagerLinux import AutostartManagerLinux
            return AutostartManagerLinux(filesystemHelper, config, argParser, logger)

    def _getClipboardManager(
        self,
        osSwitch: OSSwitch,
        eventService: EventService,
        logger: Logger,
        modalWindowManager: ModalWindowManager,
    ) -> ClipboardManager:
        if osSwitch.isMacOS():
            from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
            return ClipboardManagerMacOs(eventService, logger)
        else:
            from src.Service.ClipboardManagerLinux import ClipboardManagerLinux
            return ClipboardManagerLinux(eventService, logger, modalWindowManager)

    def _getStatusbarApp(
        self,
        osSwitch: OSSwitch,
        timestampTextFormatter: TimestampTextFormatter,
        clipboardManager: ClipboardManager,
        conversionManager: ConversionManager,
        events: EventService,
        config: Configuration,
        configFileManager: ConfigFileManager,
        autostartManager: AutostartManager,
        updateManager: UpdateManager,
        modalWindowManager: ModalWindowManager,
        logger: Logger,
        debug: Debug,
    ) -> StatusbarApp:
        if osSwitch.isMacOS():
            from src.Service.StatusbarAppMacOs import StatusbarAppMacOs
            return StatusbarAppMacOs(
                osSwitch,
                timestampTextFormatter,
                clipboardManager,
                conversionManager,
                events,
                config,
                configFileManager,
                autostartManager,
                updateManager,
                modalWindowManager,
                logger,
                debug,
            )
        else:
            from src.Service.StatusbarAppLinux import StatusbarAppLinux
            return StatusbarAppLinux(
                osSwitch,
                timestampTextFormatter,
                clipboardManager,
                conversionManager,
                events,
                config,
                configFileManager,
                autostartManager,
                updateManager,
                modalWindowManager,
                logger,
                debug,
            )
