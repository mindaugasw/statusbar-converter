from typing import Callable


class MenuItem:
    label: str | None
    isDisabled: bool
    isSeparator: bool
    callback: Callable | None
    initialState: bool | None
    nativeItem = None

    def __init__(
        self,
        label: str | None = None,
        isDisabled=False,
        isSeparator=False,
        initialState: bool | None = None,
        callback: Callable | None = None,
    ):
        if isSeparator and (label or isDisabled or callback):
            raise Exception('Invalid MenuItem creation: separator item cannot have any other properties')

        if not isSeparator and not label:
            raise Exception('Invalid MenuItem creation: all non-separator items must have label')

        if isDisabled and callback:
            raise Exception('Invalid MenuItem creation: disabled item cannot have callback')

        self.label = label
        self.isDisabled = isDisabled
        self.isSeparator = isSeparator
        self.initialState = initialState
        self.callback = callback

    def setNativeItem(self, nativeItem) -> None:
        self.nativeItem = nativeItem
