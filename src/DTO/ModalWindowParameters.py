class ModalWindowParameters:
    title: str
    logCategory: str
    width: int
    height: int

    def __init__(
        self,
        title: str,
        logCategory: str,
        width: int,
        height: int,
    ):
        self.title = title
        self.logCategory = logCategory
        self.width = width
        self.height = height
