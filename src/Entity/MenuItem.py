from typing import Callable


class MenuItem:
    label: str | None
    isDisabled: bool
    isSeparator: bool
    callback: Callable | None
    nativeItem = None

    def __init__(
        self,
        label: str | None = None,
        isDisabled=False,
        isSeparator=False,
        callback: Callable | None = None,
    ):
        if isSeparator and (label or isDisabled or callback):
            raise Exception('Invalid MenuItem creation: separator item cannot have any other properties')

        if not isSeparator and not label:
            raise Exception('Invalid MenuItem creation: all non-separator items must have label')

        if isDisabled and callback:
            raise Exception('Invalid MenuItem creation: disabled item cannot have callback')

        # if not isDisabled and not callback:
        #     raise Exception('Invalid MenuItem creation: non-disabled item must have callback')

        self.label = label
        self.isDisabled = isDisabled
        self.isSeparator = isSeparator
        self.callback = callback

    def setNativeItem(self, nativeItem) -> None:
        self.nativeItem = nativeItem
