from abc import ABC
from unittest import TestCase

from src.Service.Conversion.Converter.SimpleUnit.AbstractSimpleConverter import AbstractSimpleConverter


class AbstractSimpleUnitConverterTest(TestCase, ABC):
    def _testTryConvert(
        self, converter: AbstractSimpleConverter,
        number: float, unitId: str,
        expectedSuccess: bool, expectedFrom: str | None, expectedTo: str | None,
    ):
        if unitId != unitId.lower():
            raise Exception('tryConvert function expects already lower-cased unitId')

        success, result = converter.tryConvert(number, unitId)

        self.assertEqual(expectedSuccess, success)

        if success:
            self.assertEqual(expectedFrom, result.originalText)
            self.assertEqual(expectedTo, result.convertedText)
