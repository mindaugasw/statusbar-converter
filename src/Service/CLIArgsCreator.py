import argparse
from typing import Any


# noinspection PyShadowingBuiltins
class CLIArgsCreator:
    """
    CLIArgsCreator provides a bit saner API for the built-int argparse, which is annoyingly inconsistent.

    Usage:

    parser = argparse.ArgumentParser()
    argsCreator = CLIArgsCreator(parser)
    argsCreator.addPositionalArg(...)
    parser.parse_args()
    """

    _parser: argparse.ArgumentParser

    def __init__(self, parser: argparse.ArgumentParser):
        self._parser = parser

    def addPositionalArg(
        self,
        cliName: str,
        help: str | None = None,
        codeName: str | None = None,
        choices: list[str] | None = None,
    ) -> None:
        """
        Add positional, required arg

        :param cliName: Name displayed in the terminal. This value should be without dashes -- or -
        :param help: Help text
        :param codeName: Can override name in code. Defaults to cliName
        :param choices: Allowed values list, automatically validated
        """

        if cliName.startswith('-'):
            raise Exception(
                f'cliName for positional arg must not start with a dash, give name: {cliName}'
            )

        params: dict[str, Any] = {}

        if codeName is not None:
            # cliName vs codeName for positional args:
            # By default, argparse uses 1st arg for both display and code name.
            #
            # If override is needed for code name, then use 1st value (name_or_flags param),
            # while metavar overrides display name shown in the terminal

            params['metavar'] = cliName
            cliName = codeName

        if choices is not None:
            params['choices'] = choices

        self._parser.add_argument(
            # Positional arg is when name does not have -- or - prefix
            cliName,
            help=help,
            **params,
        )

    def addOptionString(
        self,
        cliName: str | list[str],
        help: str | None = None,
        codeName: str | None = None,
        choices: list[str] | None = None,
    ) -> None:
        """
        Add optional text value arg

        :param cliName: Name displayed in the terminal, including dashes -- or -
        :param help:
        :param codeName: Can override name in code. Defaults to cliName (but without dashes)
        :param choices: Allowed values list, automatically validated
        :return:
        """

        self._addOption(
            'store',
            cliName,
            help,
            codeName,
            choices,
            False,
        )

    def addOptionBool(
        self,
        cliName: str | list[str],
        help: str | None = None,
        codeName: str | None = None,
        defaultValue: bool = False,
    ) -> None:
        """
        Add optional bool value arg (i.e. a flag)

        :param cliName: Name displayed in the terminal, including dashes -- or -
        :param help:
        :param codeName: Can override name in code. Defaults to cliName (but without dashes)
        :param defaultValue: Default value to set if flag is not provided
        """

        action = 'store_false' if defaultValue else 'store_true'

        self._addOption(
            action,
            cliName,
            help,
            codeName,
            None,
            False,
        )

    def addOptionInt(
        self,
        cliName: str | list[str],
        help: str | None = None,
        codeName: str | None = None,
        choices: list[str] | None = None,
    ) -> None:
        """
        Add optional int value arg

        :param cliName: Name displayed in the terminal, including dashes -- or -
        :param help:
        :param codeName: Can override name in code. Defaults to cliName (but without dashes)
        :param choices: Allowed values list, automatically validated
        """

        self._addOption(
            'store',
            cliName,
            help,
            codeName,
            choices,
            True,
        )

    def _addOption(
        self,
        action: str,
        cliName: str | list[str],
        help: str | None,
        codeName: str | None,
        choices: list[str] | None,
        asInt: bool,
    ) -> None:
        if isinstance(cliName, str):
            cliName = [cliName]

        for cliNameValue in cliName:
            if not cliNameValue.startswith('-'):
                raise Exception(
                    f'Invalid config for {cliName[0]} option - value must start with dash - or --'
                )

        params: dict[str, Any] = {}

        if codeName is not None:
            # cliName vs codeName for option args:
            # Here it's saner than for positional args.
            # First param is terminal display name, and dest can override code name
            params['dest'] = codeName

        if choices is not None:
            params['choices'] = choices

        if asInt:
            params['type'] = int

        self._parser.add_argument(
            # Option arg is when name has -- or - prefix
            *cliName,
            action=action,
            help=help,
            **params,
        )
