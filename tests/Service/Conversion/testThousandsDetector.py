from typing import Union, Tuple
from unittest import TestCase

from src.Service.Conversion.ThousandsDetector import ThousandsDetector


class TestThousandsDetector(TestCase):
    _testCaseType = Union[Tuple[str, int | None], Tuple[str, int | None, bool]]

    def testParseNumber(self) -> None:
        casesInitial: list[TestThousandsDetector._testCaseType] = [
            # input,          expected output,   auto-generate ,.? (Default True)
            ('100',           100,               False),
            ('10.5',          10.5),
            ('10.50',         10.5),
            ('56.123',        56123),
            # triple digit before/after separator - can be both thousand or decimal separator
            ('100.500',       100500),
            ('100.5000',      100.5),
            ('1.123.456',     1123456),
            ('1.123.456,789', 1123456.789),
            ('1.123,456,789', None),
            ('1.2.3',         None),
            ('11.22.33',      None),
            ('11.222.33',     None),
            ('11.222.333',    11222333),
            ('1234.4567,789', None),
            ('001',           1,                 False),
            ('1..5',          None),
            ('1.,5',          None),

            # (',', None), # TODO move to another test
            # ('.', None),
        ]
        cases = self._generateTestCases(casesInitial)

        correctResults = 0
        casesCount = len(cases)
        output = '\n%13s => %12s  !=  Error\n' % ('From', 'Expected')
        parser = ThousandsDetector()

        for case in cases:
            result = parser.parseNumber(case[0])
            output += '%13s => %12s' % (case[0], case[1])

            if result != case[1]:
                output += '  != %12s\n' % result
            else:
                output += '\n'
                correctResults += 1

        output += f'Correct: {correctResults}/{casesCount}\n'

        self.assertEqual(casesCount, correctResults, output)

    def _generateTestCases(self, cases: list[_testCaseType]) -> list[_testCaseType]:
        """
        Generate more test cases by swapping , and . in original test cases
        """

        convertedList: list[TestThousandsDetector._testCaseType] = []

        for case in cases:
            convertedList.append(case)

            if len(case) > 2 and case[2] == False:
                continue

            convertedText = case[0].replace(',', '#').replace('.', ',').replace('#', '.')
            convertedList.append((convertedText, case[1]))

        return convertedList
