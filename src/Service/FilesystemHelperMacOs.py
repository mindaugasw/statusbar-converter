import os
import re
import rumps
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp


class FilesystemHelperMacOs(FilesystemHelper):
    def getUserDataDir(self) -> str:
        return rumps.application_support(StatusbarApp.APP_NAME)

    @staticmethod
    def getAppPath() -> str | None:
        projectDir = FilesystemHelper.getProjectDir()

        result = re.search('^.+\\.app', projectDir, re.IGNORECASE)

        if result is None:
            return None

        return result.group()
