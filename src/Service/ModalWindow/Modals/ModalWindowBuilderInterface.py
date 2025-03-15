from abc import ABC, abstractmethod

from src.DTO.ModalWindowParameters import ModalWindowParameters


class ModalWindowBuilderInterface(ABC):
    @abstractmethod
    def getParameters(self) -> ModalWindowParameters:
        pass

    @abstractmethod
    def reinitializeState(self) -> None:
        pass

    @abstractmethod
    def build(self, arguments: dict[str, any]) -> None:
        pass
