from requests import Response

from src.DTO.Exception.FormatableExceptionInterface import FormatableExceptionInterface


class InvalidHTTPResponseException(Exception, FormatableExceptionInterface):
    _response: Response

    def __init__(self, message: str, response: Response):
        super().__init__(message)

        self._response = response

    def formatExceptionData(self) -> str:
        return (
            f'Response status code: {self._response.status_code}\n'
            f'Response payload:\n{self._response.text}'
        )
