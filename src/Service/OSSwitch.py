import platform


class OSSwitch:
    OS_MAC_OS = 'Darwin'
    OS_LINUX = 'Linux'

    os: str

    def __init__(self):
        self.os = platform.system()

        if not self.isMacOS() and not self.isLinux():
            raise Exception('Unsupported OS: ' + self.os)

    def isMacOS(self) -> bool:
        return self.os == OSSwitch.OS_MAC_OS

    def isLinux(self) -> bool:
        return self.os == OSSwitch.OS_LINUX
