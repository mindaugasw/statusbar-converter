import datetime
import os.path
import random
import string
import subprocess
import time

from src.Service.FilesystemHelper import FilesystemHelper


class Logger:
    LOG_FILE_TRUNCATE_LENGTH = 1000

    # static
    instance = None

    _logPath: str
    _isDebugEnabled: bool
    _instanceId: str

    def __init__(self, filesystemHelper: FilesystemHelper):
        self._isDebugEnabled = False
        self._logPath = f'{filesystemHelper.getUserDataDir()}/log.txt'
        self._initializeLogFile()
        self._instanceId = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        Logger.instance = self

        self.logRaw('\n\n')
        self.log(f'[Start] Starting app @ {datetime.date.today().isoformat()}')

    def log(self, content) -> None:
        message = '%s-%s: %s\n' % (time.strftime('%H:%M:%S'), self._instanceId, str(content))
        self.logRaw(message)

    def logRaw(self, content: str) -> None:
        print(content, end='')

        with open(self._logPath, 'a') as file:
            file.write(str(content))

    def logDebug(self, content) -> None:
        if self._isDebugEnabled:
            self.log(content)

    def setDebugEnabled(self, enabled: bool) -> None:
        # Separate setter needed (instead of injecting Debug class) to allow using
        # Logger before Debug (ant its many dependencies) are fully initialized
        self._isDebugEnabled = enabled

    def _initializeLogFile(self) -> None:
        if os.path.isdir(self._logPath):
            raise Exception('Cannot create log file, path is a directory: ' + self._logPath)

        if os.path.exists(self._logPath):
            self._truncateLogFile()

    def _truncateLogFile(self) -> None:
        tempLogPath = self._logPath + '.tmp'
        subprocess.call(f'tail -n {Logger.LOG_FILE_TRUNCATE_LENGTH} "{self._logPath}" > "{tempLogPath}"', shell=True)
        os.remove(self._logPath)
        os.rename(tempLogPath, self._logPath)
