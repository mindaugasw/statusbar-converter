import inspect
import types
from types import UnionType
from typing import TypeVar

from src.DTO.Exception.ServiceCreateException import ServiceCreateException
from src.Type.Types import ServiceOverrides, ArgumentOverrides

T = TypeVar('T')


class DependencyManager:
    _services: dict[type, object]
    _serviceOverrides: ServiceOverrides
    _argumentOverrides: ArgumentOverrides

    def __init__(
        self,
        serviceOverrides: ServiceOverrides | None = None,
        argumentOverrides: ArgumentOverrides | None = None,
    ):
        self._services = {}
        self[DependencyManager] = self

        self._serviceOverrides = serviceOverrides if serviceOverrides is not None else {}
        self._argumentOverrides = argumentOverrides if argumentOverrides is not None else {}

    def __getitem__(self, key: type[T]) -> T:
        if key not in self._services:
            self[key] = self._createService(key)

        return self._services[key]  # type: ignore[return-value]

    def __setitem__(self, key: type[T], service: T) -> None:
        if key in self._services:
            raise Exception(f'Service "{key.__name__}" already exists in the container')

        self._services[key] = service

    def _createService(self, key: type[T]) -> T:
        # Check service overrides
        if key in self._serviceOverrides:
            service = self._serviceOverrides[key](self)

            if not isinstance(service, key):
                raise ServiceCreateException(
                    key,
                    f'received non-matching overridden type "{type(service).__name__}"',
                )

            return service

        # Prepare arguments
        signature = inspect.signature(key.__init__)
        kwargs = {}

        for name, param in signature.parameters.items():
            # Check for default params
            # 'args' and 'kwargs' are auto added for classes without constructor
            # 'obj' and 'keywords' are auto added by PyPy
            if (
                (name == 'self' or name == 'args' or name == 'kwargs' or name == 'obj' or name == 'keywords')
                and param.default is param.empty and param.annotation is param.empty
            ):
                continue

            paramType = param.annotation

            # Check argument overrides
            if key in self._argumentOverrides and name in self._argumentOverrides[key]:
                argOverride = self._argumentOverrides[key][name](self)

                if paramType is not None:
                    if not isinstance(paramType, types.GenericAlias) and not isinstance(argOverride, paramType):
                        # Generic types (e.g. dict[str, int]) don't work with `isinstance()`.
                        # Thus we first check if type is generic before checking the actual type validity

                        raise ServiceCreateException(
                            key,
                            f'received non-matching overridden arg type: for "{name}" received '
                            f'"{type(argOverride).__name__}" instead of expected "{paramType.__name__}"',
                        )

                kwargs[name] = argOverride

                continue

            # Check if param is union type
            if isinstance(paramType, UnionType):
                raise ServiceCreateException(
                    key,
                    f'union param "{name}" is not supported, please manually override it',
                )

            # Check if param type is scalar builtin
            if paramType is None or paramType.__module__ == 'builtins':
                # Use default param value if available
                if param.default is not param.empty:
                    continue

                raise ServiceCreateException(
                    key,
                    f'param "{name}" must be type-hinted and non-scalar or manually overridden. '
                    f'Param type is "{paramType.__name__ if paramType is not None else None}"',
                )

            # Get or create a new service
            kwargs[name] = self[paramType]

        return key(**kwargs)
