import os
from src.Service.FilesystemHelper import FilesystemHelper
from src.Service.StatusbarApp import StatusbarApp


class FilesystemHelperLinux(FilesystemHelper):
    def getUserDataDir(self) -> str:
        path = os.path.expanduser(f'~/.config/{StatusbarApp.APP_NAME}')
        os.makedirs(path, exist_ok=True)

        return path

    @staticmethod
    def getAppPath() -> str | None:
        # TODO implement
        pass
