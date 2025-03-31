import os
import subprocess
import sys

from src.Constant.AppConstant import AppConstant
from src.Service.FilesystemHelper import FilesystemHelper


class FilesystemHelperLinux(FilesystemHelper):
    def getUserDataDir(self) -> str:
        path = os.path.expanduser(f'~/.config/{AppConstant.APP_NAME}')
        os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def getAppExecutablePath() -> str | None:
        if not FilesystemHelper.isPackagedApp():
            return None

        return sys.executable

    @staticmethod
    def getStartupScriptDir() -> str:
        path = os.path.expanduser('~/.config/autostart')
        os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def openFile(filePath: str) -> None:
        subprocess.call(['xdg-open', filePath])
