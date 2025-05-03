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

    def getAppExecutablePath(self) -> str | None:
        if not self.isPackagedApp():
            return None

        return sys.executable

    def getStartupScriptDir(self) -> str:
        path = os.path.expanduser('~/.config/autostart')
        os.makedirs(path, exist_ok=True)

        return path

    def openFile(self, filePath: str) -> None:
        subprocess.call(['xdg-open', filePath])
