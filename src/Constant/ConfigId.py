class ConfigId:
    # Config keys
    ClearOnChange = ['clear_on_change']
    ClearAfterTime = ['clear_after_time']
    FlashIconOnChange = ['flash_icon_on_change']
    Debug = ['debug']

    Converter_Distance_Enabled = ['converters', 'distance', 'enabled']
    Converter_Distance_PrimaryUnit_Metric = ['converters', 'distance', 'primary_unit_metric']

    Converter_Temperature_Enabled = ['converters', 'temperature', 'enabled']
    Converter_Temperature_PrimaryUnit = ['converters', 'temperature', 'primary_unit']

    Converter_Timestamp_Enabled = ['converters', 'timestamp', 'enabled']
    Converter_Timestamp_IconFormat = ['converters', 'timestamp', 'icon_text_format']
    Converter_Timestamp_Menu_LastConversion_OriginalText = ['converters', 'timestamp', 'menu_items_last_conversion', 'original_text']
    Converter_Timestamp_Menu_LastConversion_ConvertedText = ['converters', 'timestamp', 'menu_items_last_conversion', 'converted_text']
    Converter_Timestamp_Menu_CurrentTimestamp = ['converters', 'timestamp', 'menu_items_current_timestamp']

    Converter_Volume_Enabled = ['converters', 'volume', 'enabled']
    Converter_Volume_PrimaryUnit_Metric = ['converters', 'volume', 'primary_unit_metric']

    Converter_Weight_Enabled = ['converters', 'weight', 'enabled']
    Converter_Weight_PrimaryUnit_Metric = ['converters', 'weight', 'primary_unit_metric']

    # Data keys
    Data_Update_SkipVersion = ['update', 'skip_version']
    Data_Autostart_Enabled = ['auto_run', 'enabled']
    Data_Autostart_InitialSetupComplete = ['auto_run', 'initial_setup_complete']
