from typing import Callable, Any, Final, Type, Tuple

import dearpygui.dearpygui as dpg

from src.Constant.AppConstant import AppConstant
from src.Constant.ConfigId import ConfigId
from src.Constant.CurrencyCategory import CurrencyCategory
from src.Constant.Logs import Logs
from src.DTO.ConfigParameter import ConfigParameter
from src.DTO.Converter.CurrencyUnit import CurrencyUnit
from src.DTO.Converter.UnitDefinition import UnitDefinition
from src.DTO.ModalWindowParameters import ModalWindowParameters
from src.DTO.SettingsModal.AbstractControlProperties import AbstractControlProperties
from src.DTO.SettingsModal.CheckboxControlProperties import CheckboxControlProperties
from src.DTO.SettingsModal.DropdownControlProperties import DropdownControlProperties
from src.DTO.SettingsModal.RadioControlProperties import RadioControlProperties
from src.DTO.SettingsModal.TextControlProperties import TextControlProperties
from src.Service.ConfigFileManager import ConfigFileManager
from src.Service.Configuration import Configuration
from src.Service.Conversion.Unit.Currency.CurrencyConverter import CurrencyConverter
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.Logger import Logger
from src.Service.ModalWindow.BuilderHelper import BuilderHelper
from src.Service.ModalWindow.Modals.ModalWindowBuilderInterface import ModalWindowBuilderInterface
from src.Type.Types import DpgTag, SettingsRadioValues


class SettingsBuilder(ModalWindowBuilderInterface):
    _WINDOW_WIDTH: Final = 600
    _PRIMARY_TAG: Final = 'primary'
    _PRIORITY_SORT_CURRENCIES: Final = ['eur', 'usd', 'gbp']

    _SPACER_LEFT_INDENT_WIDTH: Final = 1
    _SPACER_SECTION_TOP_HEIGHT: Final = 3
    _SPACER_SECTION_INNER_HEIGHT: Final = 10
    _SPACER_SECTION_BOTTOM_HEIGHT: Final = 15

    _config: Configuration
    _configFileManager: ConfigFileManager
    _filesystemHelper: FilesystemHelper
    _currencyConverter: CurrencyConverter
    _logger: Logger

    _controls: dict[DpgTag, AbstractControlProperties]
    _appRestartNoteDefaultTag: DpgTag
    _appRestartNoteEditedTag: DpgTag
    _appRestartNoteChanged: bool

    def __init__(
        self,
        config: Configuration,
        configFileManager: ConfigFileManager,
        filesystemHelper: FilesystemHelper,
        currencyConverter: CurrencyConverter,
        logger: Logger,
    ):
        self._config = config
        self._configFileManager = configFileManager
        self._filesystemHelper = filesystemHelper
        self._currencyConverter = currencyConverter
        self._logger = logger

    def getParameters(self) -> ModalWindowParameters:
        return ModalWindowParameters(
            'Settings',
            'Settings',
            self._WINDOW_WIDTH,
            600,
            self._PRIMARY_TAG,
        )

    def reinitializeState(self) -> None:
        self._controls = {}
        self._appRestartNoteDefaultTag = -1
        self._appRestartNoteEditedTag = -1
        self._appRestartNoteChanged = False

    def build(self, arguments: dict[str, Any]) -> None:
        BuilderHelper.registerHyperlinkTheme()

        with dpg.window(label='Window title', tag=self._PRIMARY_TAG, on_close=self._onClose):
            self._buildHeader()
            self._buildCollapsableSection('General settings', self._buildGeneralSettings)
            self._buildCollapsableSection('Currency converter settings', self._buildCurrencyConverterSettings)
            self._buildCollapsableSection('Distance converter settings', self._buildDistanceConverterSettings)
            self._buildCollapsableSection('Temperature converter settings', self._buildTemperatureConverterSettings)
            self._buildCollapsableSection('Volume converter settings', self._buildVolumeConverterSettings)
            self._buildCollapsableSection('Weight converter settings', self._buildWeightConverterSettings)
            self._buildCollapsableSection('Unix timestamp converter settings', self._buildTimestampConverterSettings)

    def _buildHeader(self) -> None:
        with dpg.group(horizontal=True):
            with dpg.group():
                BuilderHelper.addImage(self._filesystemHelper.getAssetsDir() + '/icon_colored_small.png')

            with dpg.group():
                dpg.add_text('Settings')
                dpg.add_text('v' + self._config.getAppVersion(), pos=[self._WINDOW_WIDTH - 55, 8])

                dpg.add_spacer(height=5)

                # Seems like it's impossible to change text color. So we create 2 labels, 1 hidden, and then switch them
                noteText = 'App needs to be restarted for changes to take effect.'
                self._appRestartNoteDefaultTag = dpg.add_text(noteText)
                self._appRestartNoteEditedTag = dpg.add_text(noteText, show=False, color=BuilderHelper.COLOR_TEXT_RED)

                dpg.add_spacer(height=25)

    def _buildCollapsableSection(self, title: str, buildContentCallback: Callable[[], None]) -> None:
        with dpg.collapsing_header(label=title):
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_spacer(width=self._SPACER_LEFT_INDENT_WIDTH)

                with dpg.group():
                    dpg.add_spacer(height=self._SPACER_SECTION_TOP_HEIGHT)

                    buildContentCallback()

                    dpg.add_spacer(height=self._SPACER_SECTION_BOTTOM_HEIGHT)

    def _buildGeneralSettings(self) -> None:
        self._registerCheckboxControl(
            dpg.add_checkbox(label='Flash statusbar icon on successful conversion'),
            ConfigId.FlashIconOnChange,
        )

        self._registerCheckboxControl(
            dpg.add_checkbox(label='Clear statusbar text on clipboard change'),
            ConfigId.ClearOnChange,
        )

        self._registerTextControl(
            dpg.add_input_int(
                label='Automatically clear statusbar text after this many seconds',
                width=50,
                min_value=0,
                max_value=3600,
                step=0,
                step_fast=0,
                min_clamped=True,
                max_clamped=True,
            ),
            ConfigId.ClearAfterTime,
            int,
        )
        BuilderHelper.addHelpText(
            'Enter zero to disable automatic text clearing.\n'
            'Default is 300 seconds (5 minutes).',
        )

    def _buildCurrencyConverterSettings(self) -> None:
        with dpg.group(horizontal=True):
            dpg.add_text('Supports converting currencies like')
            dpg.add_text('5 $', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('89 CAD', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(', some cryptocurrencies like')
            dpg.add_text('0.08 BTC', color=BuilderHelper.COLOR_TEXT_BLUE)

        dpg.add_spacer(height=self._SPACER_SECTION_INNER_HEIGHT)

        self._registerCheckboxControl(dpg.add_checkbox(label='Enabled'), ConfigId.Converter_Currency_Enabled)

        currencies = self._currencyConverter.getUnitsDefinition()

        with dpg.group(horizontal=True):
            dpg.add_text('Convert to currency:')

            if len(currencies) == 0:
                dpg.add_combo([], enabled=False, height_mode=dpg.mvComboHeight_Large),
            else:
                currenciesSorted = dict(sorted(currencies.items(), key=self._currenciesSorter))
                dropdownItems = {code: f'{code.upper()} - {definition.unit.name}' for code, definition in currenciesSorted.items()}
                dropdownNames = list(dropdownItems.values())

                self._registerDropdownControl(
                    dpg.add_combo(dropdownNames, height_mode=dpg.mvComboHeight_Large),
                    ConfigId.Converter_Currency_PrimaryCurrency,
                    dropdownItems,
                )

        if len(currencies) == 0:
            dpg.add_text(
                'Currency converter is not yet initialized, cannot choose primary currency.\n'
                'Try restarting the app.',
                color=BuilderHelper.COLOR_TEXT_RED,
            )

    def _buildMetricImperialConverterSettings(
        self,
        descriptionBuilder: Callable[[], None],
        enabledConfigId: ConfigParameter,
        primaryUnitConfigId: ConfigParameter,
        primaryUnitRadioValues: SettingsRadioValues,
        primaryUnitControlLabel: str,
    ) -> None:
        with dpg.group(horizontal=True):
            descriptionBuilder()

        dpg.add_spacer(height=self._SPACER_SECTION_INNER_HEIGHT)

        self._registerCheckboxControl(dpg.add_checkbox(label='Enabled'), enabledConfigId)

        with dpg.group(horizontal=True):
            dpg.add_text('Convert to units:')

            self._registerRadioControl(
                dpg.add_radio_button(
                    list(primaryUnitRadioValues.keys()),
                    label=primaryUnitControlLabel,
                    horizontal=True,
                ),
                primaryUnitConfigId,
                primaryUnitRadioValues,
            )

    def _buildDistanceConverterSettings(self) -> None:
        def _distanceDescriptionBuilder() -> None:
            dpg.add_text('Supports converting units like')
            dpg.add_text('5 km', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('9.7 miles', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('3 ft', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('6"', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text('.')

        self._buildMetricImperialConverterSettings(
            _distanceDescriptionBuilder,
            ConfigId.Converter_Distance_Enabled,
            ConfigId.Converter_Distance_PrimaryUnit_Metric,
            {'Metric': True, 'Imperial': False},
            'radio_distanceConverter_primaryUnit_isMetric',
        )

    def _buildTemperatureConverterSettings(self) -> None:
        def _temperatureDescriptionBuilder() -> None:
            dpg.add_text('Supports converting units like')
            dpg.add_text('22 °C', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text('or')
            dpg.add_text('60 Fahrenheit', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text('.')

        self._buildMetricImperialConverterSettings(
            _temperatureDescriptionBuilder,
            ConfigId.Converter_Temperature_Enabled,
            ConfigId.Converter_Temperature_PrimaryUnit_Celsius,
            {'Celsius': True, 'Fahrenheit': False},
            'radio_temperatureConverter_primaryUnit_isCelsius',
        )

    def _buildVolumeConverterSettings(self) -> None:
        def _volumeDescriptionBuilder() -> None:
            dpg.add_text('Supports converting units like')
            dpg.add_text('500 ml', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('60 mm3', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('3 tbsp', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('80 fl oz', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('20 gal', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text('.')

        self._buildMetricImperialConverterSettings(
            _volumeDescriptionBuilder,
            ConfigId.Converter_Volume_Enabled,
            ConfigId.Converter_Volume_PrimaryUnit_Metric,
            {'Metric': True, 'Imperial': False},
            'radio_volumeConverter_primaryUnit_isMetric',
        )

    def _buildWeightConverterSettings(self) -> None:
        def _weightDescriptionBuilder() -> None:
            dpg.add_text('Supports converting units like')
            dpg.add_text('50 kg', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('8 ton', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('18 lbs', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('4.5 st', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text('.')

        self._buildMetricImperialConverterSettings(
            _weightDescriptionBuilder,
            ConfigId.Converter_Weight_Enabled,
            ConfigId.Converter_Weight_PrimaryUnit_Metric,
            {'Metric': True, 'Imperial': False},
            'radio_weightConverter_primaryUnit_isMetric',
        )

    def _buildTimestampConverterSettings(self) -> None:
        with dpg.group(horizontal=True):
            dpg.add_text('Supports converting timestamps like')
            dpg.add_text('1745129166', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text(',')
            dpg.add_text('1745129166000', color=BuilderHelper.COLOR_TEXT_BLUE)
            dpg.add_text('.')

        dpg.add_spacer(height=self._SPACER_SECTION_INNER_HEIGHT)
        self._registerCheckboxControl(dpg.add_checkbox(label='Enabled'), ConfigId.Converter_Timestamp_Enabled)
        dpg.add_spacer(height=self._SPACER_SECTION_INNER_HEIGHT)

        with dpg.tree_node(label='Advanced unix timestamp settings'):
            dpg.add_spacer(height=self._SPACER_SECTION_TOP_HEIGHT)
            dpg.add_text(
                'More timestamp settings (e.g. shown date formats) can be configured by manually editing '
                'configuration files. '
                'Note, that invalid configuration can break the app. '
                'Also, user configuration will not be automatically updated and can break future app versions.'
                '\n\n',
                wrap=self._WINDOW_WIDTH - 70,
            )

            dpg.add_text('Configuration can be edited in the file:')
            BuilderHelper.addHyperlink(
                self._configFileManager.getUserConfigPath(),
                lambda: self._filesystemHelper.openFile(self._configFileManager.getUserConfigPath()),
            )

            url = AppConstant.WEBSITE + '/blob/master/config/config.app.yml'
            dpg.add_text('\nAll supported configuration reference is available at:')
            BuilderHelper.addHyperlink(
                'github.com/mindaugasw/statusbar-converter/.../config/config.app.yml',
                url,
            )

    def _registerTextControl(self, tag: DpgTag, configId: ConfigParameter, castToType: Type) -> None:
        dpg.set_item_callback(tag, self._controlCallback)
        dpg.set_value(tag, self._config.get(configId))
        self._controls[tag] = TextControlProperties(configId, castToType)

    def _registerCheckboxControl(self, tag: DpgTag, configId: ConfigParameter) -> None:
        dpg.set_item_callback(tag, self._controlCallback)
        dpg.set_value(tag, self._config.get(configId))
        self._controls[tag] = CheckboxControlProperties(configId)

    def _registerRadioControl(self, tag: DpgTag, configId: ConfigParameter, radioValues: SettingsRadioValues) -> None:
        radioValuesInverted = {v: k for k, v in radioValues.items()}
        selectedValue = radioValuesInverted[self._config.get(configId)]

        dpg.set_item_callback(tag, self._controlCallback)
        dpg.set_value(tag, selectedValue)
        self._controls[tag] = RadioControlProperties(configId, radioValues)

    def _registerDropdownControl(self, tag: DpgTag, configId: ConfigParameter, valueToNameMap: dict[str, str]) -> None:
        dpg.set_item_callback(tag, self._controlCallback)
        initialValue = valueToNameMap[self._config.get(configId)]
        dpg.set_value(tag, initialValue)

        nameToValueMap = {value: key for key, value in valueToNameMap.items()}
        self._controls[tag] = DropdownControlProperties(configId, nameToValueMap)

    def _controlCallback(self, sender: DpgTag, appData, userData) -> None:
        controlProperties: AbstractControlProperties = self._controls[sender]
        value: Any

        if isinstance(controlProperties, CheckboxControlProperties):
            value = bool(appData)
        elif isinstance(controlProperties, TextControlProperties):
            value = controlProperties.castToType(appData)
        elif isinstance(controlProperties, RadioControlProperties):
            value = controlProperties.radioValues[appData]
        elif isinstance(controlProperties, DropdownControlProperties):
            value = controlProperties.nameToValueMap[appData]
        else:
            raise Exception(f'Unknown control properties type: {type(controlProperties).__name__}')

        label = dpg.get_item_label(sender)
        self._logger.log(f'{Logs.catSettings}Callback #{sender} ({label}) with data: {value} ({type(value).__name__})')

        self._config.set(controlProperties.configId, value)

        if self._appRestartNoteChanged is False:
            dpg.hide_item(self._appRestartNoteDefaultTag)
            dpg.show_item(self._appRestartNoteEditedTag)
            self._appRestartNoteChanged = True

    def _onClose(self) -> None:
        BuilderHelper.deleteHyperlinkTheme()

    def _currenciesSorter(self, item: Tuple[str, UnitDefinition[CurrencyUnit]]) -> str:
        currency = item[1].unit
        categoryPrefix = '0' if currency.category == CurrencyCategory.FIAT else '1'
        priorityPrefix = '0' if currency.primaryAlias in self._PRIORITY_SORT_CURRENCIES else '1'

        return categoryPrefix + priorityPrefix + currency.primaryAlias
