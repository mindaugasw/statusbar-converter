from typing import TypeVar

class ServiceContainer:
    T = TypeVar('T')

    _services: dict[type, object]

    def __init__(self):
        self._services = {}

    def __getitem__(self, key: type[T]) -> T:
        if key not in self._services:
            raise Exception(f'Service with id "{key}" not found in the container')

        return self._services[key]  # type: ignore[return-value]

    def __setitem__(self, key: type[T], service: T) -> None:
        if key in self._services:
            raise Exception(f'Service with id "{key}" already exists in the container')

        self._services[key] = service
