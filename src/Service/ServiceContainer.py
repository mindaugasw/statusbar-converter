from typing import TypeVar

from src.Constant.ModalId import ModalId
from src.Service.AppLoop import AppLoop
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Conversion.ConversionManager import ConversionManager
from src.Service.Conversion.ConverterInterface import ConverterInterface
from src.Service.Conversion.Timestamp.TimestampConverter import TimestampConverter
from src.Service.Conversion.Timestamp.TimestampTextFormatter import TimestampTextFormatter
from src.Service.Conversion.Unit.Currency.ConversionRateUpdater import ConversionRateUpdater
from src.Service.Conversion.Unit.Currency.CurrencyConverter import CurrencyConverter
from src.Service.Conversion.Unit.MetricImperial.DistanceConverter import DistanceConverter
from src.Service.Conversion.Unit.MetricImperial.TemperatureConverter import TemperatureConverter
from src.Service.Conversion.Unit.MetricImperial.VolumeConverter import VolumeConverter
from src.Service.Conversion.Unit.MetricImperial.WeightConverter import WeightConverter
from src.Service.Conversion.Unit.ThousandsDetector import ThousandsDetector
from src.Service.Conversion.Unit.UnitConverter import UnitConverter
from src.Service.Conversion.Unit.UnitConverterInterface import UnitConverterInterface
from src.Service.Conversion.Unit.UnitParser import UnitParser
from src.Service.Conversion.Unit.UnitToConverterMapper import UnitToConverterMapper
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

    def __getitem__(self, item: type[T]) -> T:
        if item not in self._services:
            raise Exception(f'Service with id "{item}" not found in the container')

        return self._services[item]  # type: ignore[return-value]

    def initializeServices(self) -> 'ServiceContainer':
        _: dict[type, object] = {}

        # Core services
        _[OSSwitch] = osSwitch = OSSwitch()
        _[FilesystemHelper] = filesystemHelper = self._getFilesystemHelper(osSwitch)
        _[Logger] = logger = Logger(filesystemHelper)

        logger.logRaw(filesystemHelper.getInitializationLogs())
        ExceptionHandler.initialize()

        _[ConfigFileManager] = configFileManager = ConfigFileManager(filesystemHelper, logger)
        _[Configuration] = config = Configuration(filesystemHelper, configFileManager, logger)
        _[ArgumentParser] = argumentParser = ArgumentParser()
        _[Debug] = debug = Debug(config, argumentParser)
        _[EventService] = events = EventService()

        # Conversion services
        _[TimestampTextFormatter] = timestampTextFormatter = TimestampTextFormatter(config)
        _[ConversionManager] = conversionManager = self.getConversionManager(_, filesystemHelper, timestampTextFormatter, argumentParser, config, logger, osSwitch, events, debug)

        # GUI services
        _[list[ModalWindowBuilderInterface]] = modalWindowBuilders = self._getModalWindowBuilders(config, configFileManager, filesystemHelper, logger)
        _[ModalWindowManager] = modalWindowManager = ModalWindowManager(modalWindowBuilders, filesystemHelper, osSwitch, logger)

        # App services
        _[UpdateManager] = updateManager = UpdateManager(filesystemHelper, events, config, logger, debug)
        _[AutostartManager] = autostartManager = self._getAutostartManager(osSwitch, filesystemHelper, config, argumentParser, logger)
        _[ClipboardManager] = clipboardManager = self._getClipboardManager(osSwitch, events, logger, modalWindowManager, filesystemHelper)
        _[StatusbarApp] = statusbarApp = self._getStatusbarApp(osSwitch, timestampTextFormatter, clipboardManager, conversionManager, events, config, configFileManager, autostartManager, updateManager, modalWindowManager, filesystemHelper, logger, debug)
        _[AppLoop] = appLoop = self._getAppLoop(osSwitch, events, clipboardManager)

        self._services = _

        return self

    def _getFilesystemHelper(self, osSwitch: OSSwitch) -> FilesystemHelper:
        if osSwitch.isMacOS():
            from src.Service.FilesystemHelperMacOs import FilesystemHelperMacOs
            return FilesystemHelperMacOs()
        else:
            from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
            return FilesystemHelperLinux()

    def getConversionManager(
        self,
        container: dict[type, object],
        filesystemHelper: FilesystemHelper,
        timestampTextFormatter: TimestampTextFormatter,
        argumentParser: ArgumentParser,
        config: Configuration,
        logger: Logger,
        osSwitch: OSSwitch,
        events: EventService,
        debug: Debug,
    ) -> ConversionManager:
        currencyConverter = CurrencyConverter(events, config, logger)
        container[ConversionRateUpdater] = conversionRateUpdater = ConversionRateUpdater(currencyConverter, filesystemHelper, argumentParser, config, events, osSwitch, logger)

        unitBeforeConverters: list[UnitConverterInterface] = [
            currencyConverter,
        ]

        unitAfterConverters: list[UnitConverterInterface] = [
            DistanceConverter(config),
            VolumeConverter(config),
            WeightConverter(config),
            TemperatureConverter(config),
            currencyConverter,
        ]

        unitToConverterMapper = UnitToConverterMapper(unitBeforeConverters, unitAfterConverters, events)

        thousandsDetector = ThousandsDetector()
        unitParser = UnitParser(unitToConverterMapper, thousandsDetector)

        converters: list[ConverterInterface] = [
            TimestampConverter(timestampTextFormatter, config, logger),
            UnitConverter(unitParser),
        ]

        return ConversionManager(converters, events, config, logger, debug)

    def _getModalWindowBuilders(
        self,
        config: Configuration,
        configFileManager: ConfigFileManager,
        filesystemHelper: FilesystemHelper,
        logger: Logger,
    ) -> dict[str, ModalWindowBuilderInterface]:
        customizedDialogBuilder = CustomizedDialogBuilder(filesystemHelper)

        return {
            ModalId.DEMO: DemoBuilder(),
            ModalId.SETTINGS: SettingsBuilder(config, configFileManager, filesystemHelper, logger),
            ModalId.ABOUT: AboutBuilder(filesystemHelper, config),
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
        filesystemHelper: FilesystemHelper,
    ) -> ClipboardManager:
        if osSwitch.isMacOS():
            from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
            return ClipboardManagerMacOs(eventService, logger)
        else:
            from src.Service.ClipboardManagerLinux import ClipboardManagerLinux
            return ClipboardManagerLinux(eventService, logger, modalWindowManager, filesystemHelper)

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
        filesystemHelper: FilesystemHelper,
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
                filesystemHelper,
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
                filesystemHelper,
                logger,
                debug,
            )

    def _getAppLoop(self, osSwitch: OSSwitch, events: EventService, clipboardManager: ClipboardManager) -> AppLoop:
        if osSwitch.isMacOS():
            from src.Service.AppLoopMacOs import AppLoopMacOs
            from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs

            if not isinstance(clipboardManager, ClipboardManagerMacOs):
                raise Exception('Invalid type: ClipboardManager must be macOS version')

            return AppLoopMacOs(events, clipboardManager)
        else:
            from src.Service.AppLoopLinux import AppLoopLinux
            return AppLoopLinux(events)
