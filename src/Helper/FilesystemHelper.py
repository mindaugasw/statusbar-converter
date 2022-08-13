import os


class FilesystemHelper:
    @staticmethod
    def getProjectDir() -> str:
        """Full path of project directory, without trailing slash"""

        return os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
