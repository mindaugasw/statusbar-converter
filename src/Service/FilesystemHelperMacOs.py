import rumps
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp


class FilesystemHelperMacOs(FilesystemHelper):
    def getUserDataDir(self) -> str:
        return rumps.application_support(StatusbarApp.APP_NAME)
