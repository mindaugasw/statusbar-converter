import os
import sys

from src.Constant.AppConstant import AppConstant
from src.Service.FilesystemHelper import FilesystemHelper


class FilesystemHelperLinux(FilesystemHelper):
    def getUserDataDir(self) -> str:
        path = os.path.expanduser(f'~/.config/{AppConstant.appName}')
        os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def getAppPath() -> str | None:
        if not getattr(sys, "frozen", False):
            # Frozen attribute is added to packaged app
            return None

        return sys.executable

    @staticmethod
    def getStartupScriptDir() -> str:
        path = os.path.expanduser(f'~/.config/autostart')
        os.makedirs(path, exist_ok=True)

        return path
