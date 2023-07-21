import os


class FilesystemHelper:
    def getAssetsDir(self) -> str:
        return self.getProjectDir() + '/assets'

    def getConfigDir(self) -> str:
        pass

    # TODO rename add _
    def getProjectDir(self) -> str:
        """
        Absolute path of project directory

        Relevant only in dev environment, since after packaging the app code is
        moved to a different directory relative to the project
        """

        return os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')

# TODO add here method to get temp files path, move from ConfigFileManager
