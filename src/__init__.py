import platform
import src.services as services
import sys
from src.Service.StatusbarApp import StatusbarApp


def main():
    # TODO print app version as well
    print(
        f'\n{StatusbarApp.APP_NAME}\n'
        f'Platform: {platform.platform()}\n'
        f'Detected OS: {services.osSwitch.os}\n'
        f'Python: {sys.version}\n'
    )

    services.appLoop.startLoop()
    services.statusbarApp.createApp()


main()
