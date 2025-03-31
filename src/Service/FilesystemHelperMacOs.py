import re
import subprocess

import rumps

from src.Constant.AppConstant import AppConstant
from src.Service.FilesystemHelper import FilesystemHelper


class FilesystemHelperMacOs(FilesystemHelper):
    def getUserDataDir(self) -> str:
        return rumps.application_support(AppConstant.APP_NAME)

    @staticmethod
    def getAppExecutablePath() -> str | None:
        projectDir = FilesystemHelper.getProjectDir()

        result = re.search('^.+\\.app', projectDir, re.IGNORECASE)

        if result is None:
            return None

        return result.group()

    @staticmethod
    def getStartupScriptDir() -> str:
        raise Exception('Not implemented')

    @staticmethod
    def openFile(filePath: str) -> None:
        subprocess.Popen(['open', filePath])
