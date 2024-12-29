import atexit
import os
import sys
import threading
import traceback

from src.Service.Logger import Logger


class ExceptionHandler:
    @staticmethod
    def initialize() -> None:
        pass
        sys.excepthook = ExceptionHandler.handleException
        # sys.unraisablehook works only from the main thread. For other threads,
        # each thread would need to set this on its own.
        sys.unraisablehook = ExceptionHandler.handleUnraisableException
        threading.excepthook = ExceptionHandler.handleThreadingException

        atexit.register(ExceptionHandler.handleExit)

    @staticmethod
    def handleException(exceptionType, message, trace) -> None:
        ExceptionHandler._handleException(
            'main [handleException]',
            exceptionType,
            message,
            trace,
        )

    @staticmethod
    def handleThreadingException(args) -> None:
        ExceptionHandler._handleException(
            f'{args.thread.name} [handleThreadingException]',
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
        )

    @staticmethod
    def handleUnraisableException(args) -> None:
        ExceptionHandler._handleException(
            'main [handleUnraisableException]',
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
        )

    @staticmethod
    def handleExit() -> None:
        Logger.instance.log('[Exit] Exiting app normally')

    @staticmethod
    def formatExceptionLog(message: str, exception: Exception) -> str:
        traceList = traceback.format_exception(exception)
        traceString = ''.join(traceList)

        return '%s\nType: %s\nMessage: %s\nTrace: %s' % (
            message,
            type(exception),
            exception,
            traceString,
        )

    @staticmethod
    def _handleException(threadName, exceptionType, message, trace) -> None:
        stars = '********************************************************'
        Logger.instance.logRaw(f'\n\n{stars}\n')

        traceList = traceback.format_exception(exceptionType, message, trace)
        traceString = ''.join(traceList)

        Logger.instance.log(
            f'UNHANDLED EXCEPTION:\n'
            f'Thread: {threadName}\n'
            f'Type: {exceptionType}\n'
            f'Message: {message}\n'
            f'Trace: {traceString}'
        )

        Logger.instance.logRaw(f'{stars}\n')

        # Normally sys.exist() should be used. But that exits only the current thread, not the whole application.
        # os._exit() kills the whole app. But still allows PyInstaller to clean up /tmp files
        os._exit(1)
