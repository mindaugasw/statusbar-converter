class ModalWindowParameters:
    title: str
    logCategory: str
    width: int
    height: int
    primaryWindowTag: str | None

    def __init__(
        self,
        title: str | None,
        logCategory: str,
        width: int,
        height: int,
        primaryWindowTag: str | None,
    ):
        self.title = title
        self.logCategory = logCategory
        self.width = width
        self.height = height
        self.primaryWindowTag = primaryWindowTag
