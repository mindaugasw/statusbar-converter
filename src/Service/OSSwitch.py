import platform

from typing_extensions import Final


class OSSwitch:
    _OS_MAC_OS: Final[str] = 'Darwin'
    _OS_LINUX: Final[str] = 'Linux'

    os: str

    def __init__(self):
        self.os = platform.system()

        if not self.isMacOS() and not self.isLinux():
            raise Exception('Unsupported OS: ' + self.os)

    def isMacOS(self) -> bool:
        return self.os == OSSwitch._OS_MAC_OS

    def isLinux(self) -> bool:
        return self.os == OSSwitch._OS_LINUX
