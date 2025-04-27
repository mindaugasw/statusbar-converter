from typing import Final

from src.DTO.ConfigParameter import ConfigParameter


class ConfigId:
    # State keys - configurable from app settings GUI
    FlashIconOnChange: Final = ConfigParameter.newState(
        ['general_settings', 'flash_icon_on_change'],
        True,
    )

    ClearOnChange: Final = ConfigParameter.newState(
        ['general_settings', 'clear_on_change'],
        False,
    )

    ClearAfterTime: Final = ConfigParameter.newState(
        ['general_settings', 'clear_after_time'],
        300,
    )

    Converter_Currency_Enabled: Final = ConfigParameter.newState(
        ['converters', 'currency', 'enabled'],
        True,
    )

    Converter_Currency_PrimaryCurrency: Final = ConfigParameter.newState(
        ['converters', 'currency', 'primary_currency'],
        'eur',
    )

    Converter_Distance_Enabled: Final = ConfigParameter.newState(
        ['converters', 'distance', 'enabled'],
        True,
    )

    Converter_Distance_PrimaryUnit_Metric: Final = ConfigParameter.newState(
        ['converters', 'distance', 'primary_unit_metric'],
        True,
    )

    Converter_Temperature_Enabled: Final = ConfigParameter.newState(
        ['converters', 'temperature', 'enabled'],
        True,
    )

    Converter_Temperature_PrimaryUnit_Celsius: Final = ConfigParameter.newState(
        ['converters', 'temperature', 'primary_unit_celsius'],
        True,
    )

    Converter_Timestamp_Enabled: Final = ConfigParameter.newState(
        ['converters', 'timestamp', 'enabled'],
        True,
    )

    Converter_Volume_Enabled: Final = ConfigParameter.newState(
        ['converters', 'volume', 'enabled'],
        True,
    )

    Converter_Volume_PrimaryUnit_Metric: Final = ConfigParameter.newState(
        ['converters', 'volume', 'primary_unit_metric'],
        True,
    )

    Converter_Weight_Enabled: Final = ConfigParameter.newState(
        ['converters', 'weight', 'enabled'],
        True,
    )

    Converter_Weight_PrimaryUnit_Metric: Final = ConfigParameter.newState(
        ['converters', 'weight', 'primary_unit_metric'],
        True,
    )


    # State keys - managed automatically, not configurable from app settings GUI
    Update_SkipVersion: Final = ConfigParameter.newState(
        ['update', 'skip_version'],
        None,
    )

    Autostart_Enabled: Final = ConfigParameter.newState(
        ['auto_run', 'enabled'],
        False,
    )

    Autostart_InitialSetupComplete: Final = ConfigParameter.newState(
        ['auto_run', 'initial_setup_complete'],
        False,
    )


    # Config keys - configurable in user config file
    Debug: Final = ConfigParameter.newConfig(['debug'])

    Converter_Timestamp_IconFormat: Final = ConfigParameter.newConfig(
        ['converters', 'timestamp', 'icon_text_format'],
    )

    Converter_Timestamp_Menu_LastConversion_OriginalText: Final = ConfigParameter.newConfig(
        ['converters', 'timestamp', 'menu_items_last_conversion', 'original_text'],
    )

    Converter_Timestamp_Menu_LastConversion_ConvertedText: Final = ConfigParameter.newConfig(
        ['converters', 'timestamp', 'menu_items_last_conversion', 'converted_text'],
    )

    Converter_Timestamp_Menu_CurrentTimestamp: Final = ConfigParameter.newConfig(
        ['converters', 'timestamp', 'menu_items_current_timestamp'],
    )
