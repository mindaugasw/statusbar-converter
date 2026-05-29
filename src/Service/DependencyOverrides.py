from src.Constant.ModalId import ModalId
from src.Service.AppLoop import AppLoop
from src.Service.ArgumentParser import ArgumentParser
from src.Service.AutostartManager import AutostartManager
from src.Service.ClipboardManager import ClipboardManager
from src.Service.Configuration import Configuration
from src.Service.Conversion.ConversionManager import ConversionManager
from src.Service.Conversion.ConverterInterface import ConverterInterface
from src.Service.Conversion.Timestamp.TimestampConverter import TimestampConverter
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
from src.Service.DependencyManager import DependencyManager
from src.Service.EventService import EventService
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
from src.Type.Types import ServiceOverrides, ArgumentOverrides


class DependencyOverrides:
    _osSwitch: OSSwitch

    def __init__(self, osSwitch: OSSwitch):
        self._osSwitch = osSwitch

    def getServiceOverrides(self) -> ServiceOverrides:
        return {
            # ServiceType: lambda deps: ServiceType(),

            OSSwitch: lambda deps: self._osSwitch,
            FilesystemHelper: lambda deps: self._buildFilesystemHelper(),
            ClipboardManager: lambda deps: self._buildClipboardManager(deps),
            AutostartManager: lambda deps: self._buildAutostartManager(deps),
            AppLoop: lambda deps: self._buildAppLoop(deps),
        }

    def getArgumentOverrides(self) -> ArgumentOverrides:
        return {
            # ServiceType: {
            #     'paramName': lambda deps: 'paramValue',
            # }

            ModalWindowManager: {
                'builders': lambda deps: self._getModalWindowBuilders(deps),
            },
            ConversionManager: {
                'converters': lambda deps: self._buildConverters(deps),
            }
        }

    def _buildFilesystemHelper(self) -> FilesystemHelper:
        if self._osSwitch.isMacOS():
            from src.Service.FilesystemHelperMacOs import FilesystemHelperMacOs
            return FilesystemHelperMacOs()
        else:
            from src.Service.FilesystemHelperLinux import FilesystemHelperLinux
            return FilesystemHelperLinux()

    def _buildClipboardManager(self, deps: DependencyManager) -> ClipboardManager:
        eventService = deps[EventService]
        logger = deps[Logger]

        if self._osSwitch.isMacOS():
            from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs
            return ClipboardManagerMacOs(eventService, logger)
        else:
            from src.Service.ClipboardManagerLinux import ClipboardManagerLinux
            return ClipboardManagerLinux(
                eventService,
                logger,
                deps[ModalWindowManager],
                deps[FilesystemHelper],
            )

    def _getModalWindowBuilders(self, deps: DependencyManager) -> dict[str, ModalWindowBuilderInterface]:
        return {
            ModalId.DEMO: deps[DemoBuilder],
            ModalId.SETTINGS: deps[SettingsBuilder],
            ModalId.ABOUT: deps[AboutBuilder],
            ModalId.CUSTOMIZED_DIALOG: deps[CustomizedDialogBuilder],
            ModalId.MISSING_XSEL: deps[DialogMissingXselBuilder],
        }

    def _buildAutostartManager(self, deps: DependencyManager) -> AutostartManager:
        filesystemHelper = deps[FilesystemHelper]
        config = deps[Configuration]
        argParser = deps[ArgumentParser]
        logger = deps[Logger]

        if self._osSwitch.isMacOS():
            from src.Service.AutostartManagerMacOS import AutostartManagerMacOS
            return AutostartManagerMacOS(filesystemHelper, config, argParser, logger)
        else:
            from src.Service.AutostartManagerLinux import AutostartManagerLinux
            return AutostartManagerLinux(filesystemHelper, config, argParser, logger)

    def _buildAppLoop(self, deps: DependencyManager) -> AppLoop:
        events = deps[EventService]

        if self._osSwitch.isMacOS():
            from src.Service.AppLoopMacOs import AppLoopMacOs
            from src.Service.ClipboardManagerMacOs import ClipboardManagerMacOs

            clipboardManager = deps[ClipboardManager]

            if not isinstance(clipboardManager, ClipboardManagerMacOs):
                raise Exception('Invalid type: ClipboardManager must be macOS version')

            return AppLoopMacOs(events, clipboardManager)
        else:
            from src.Service.AppLoopLinux import AppLoopLinux
            return AppLoopLinux(events)

    def _buildConverters(self, deps: DependencyManager) -> list[ConverterInterface]:
        unitBeforeConverters: list[UnitConverterInterface] = [
            deps[CurrencyConverter],
        ]
        unitAfterConverters: list[UnitConverterInterface] = [
            deps[DistanceConverter],
            deps[VolumeConverter],
            deps[WeightConverter],
            deps[TemperatureConverter],
            deps[CurrencyConverter],
        ]

        deps[UnitToConverterMapper] = unitToConverterMapper = UnitToConverterMapper(unitBeforeConverters, unitAfterConverters, deps[EventService])
        deps[UnitParser] = unitParser = UnitParser(unitToConverterMapper, deps[ThousandsDetector])
        deps[UnitConverter] = unitConverter = UnitConverter(unitParser)

        converters: list[ConverterInterface] = [
            deps[TimestampConverter],
            unitConverter,
        ]

        return converters
