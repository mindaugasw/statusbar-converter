class ConvertResult:
    iconText: str
    originalText: str
    convertedText: str
    converterName: str

    def __init__(self, iconText: str, originalText: str, convertedText: str, converterName: str):
        self.iconText = iconText
        self.originalText = originalText
        self.convertedText = convertedText
        self.converterName = converterName
