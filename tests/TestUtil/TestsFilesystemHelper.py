from src.Service.FilesystemHelper import FilesystemHelper


class TestsFilesystemHelper(FilesystemHelper):
    """
    Tests filesystem helper needed to get project root dir in tests.
    Because IDE uses different working dir based on how tests are run.
    """

    def getUserDataDir(self) -> str:
        raise Exception('Not implemented')

    def getAppExecutablePath(self) -> str | None:
        raise Exception('Not implemented')

    def getStartupScriptDir(self) -> str:
        raise Exception('Not implemented')

    def openFile(self, filePath: str) -> None:
        raise Exception('Not implemented')
