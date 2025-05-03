import re
import subprocess

import rumps

from src.Constant.AppConstant import AppConstant
from src.Service.FilesystemHelper import FilesystemHelper


class FilesystemHelperMacOs(FilesystemHelper):
    def getUserDataDir(self) -> str:
        return rumps.application_support(AppConstant.APP_NAME)

    def getAppExecutablePath(self) -> str | None:
        projectDir = self.getProjectDir()

        result = re.search('^.+\\.app', projectDir, re.IGNORECASE)

        if result is None:
            return None

        return result.group()

    def getStartupScriptDir(self) -> str:
        raise Exception('Not implemented')

    def openFile(self, filePath: str) -> None:
        subprocess.Popen(['open', filePath])
