class ConvertResult:
    iconText: str
    originalText: str
    convertedText: str

    def __init__(self, iconText: str, originalText: str, convertedText: str):
        self.iconText = iconText
        self.originalText = originalText
        self.convertedText = convertedText
