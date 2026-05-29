from typing import Callable, Any

DpgTag = str | int

DialogButtonsDict = dict[str, Callable | None]

SettingsRadioValues = dict[str, Any]


# Dependency Injection types
# "object" here is DependencyManager. Not typed due to Circular Import errors
ServiceOverrides = dict[type, Callable[[object], Any]]
ArgumentOverrides = dict[type, dict[str, Callable[[object], Any]]]
