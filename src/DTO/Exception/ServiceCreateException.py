class ServiceCreateException(Exception):
    def __init__(self, key: type, message: str):
        message = f'Could not auto-create service "{key.__name__}": {message}'

        super().__init__(message)
