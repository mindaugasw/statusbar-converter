from typing import Union, Tuple
from unittest import TestCase

from src.Service.Conversion.Unit.ThousandsDetector import ThousandsDetector


class TestThousandsDetector(TestCase):
    _testCaseType = Union[Tuple[str, int | float | None], Tuple[str, int | float | None, bool]]

    def testParseNumber(self) -> None:
        casesInitial: list[TestThousandsDetector._testCaseType] = [
            # input,          expected output,   auto-generate more cases with ,.-? (Default True)
            ('100',           100,               False),
            ('-100',          -100,              False),
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
            ('-001',          -1,                False),
            ('1..5',          None),
            ('1.,5',          None),
        ]
        cases = self._generateTestCases(casesInitial)

        correctResults = 0
        casesCount = len(cases)
        output = '\n%15s => %12s  !=  Error\n' % ('From', 'Expected')
        parser = ThousandsDetector()

        for case in cases:
            result = parser.parseNumber(case[0])
            output += '%15s => %12s' % (case[0], case[1])

            if result != case[1]:
                output += '  != %12s\n' % result
            else:
                output += '\n'
                correctResults += 1

        output += f'Correct: {correctResults}/{casesCount}\n'

        self.assertEqual(casesCount, correctResults, output)

    def _generateTestCases(self, cases: list[_testCaseType]) -> list[_testCaseType]:
        """
        Generate more test cases by swapping , and . in original test cases,
        adding negative number test case
        """

        convertedList: list[TestThousandsDetector._testCaseType] = []

        for case in cases:
            convertedList.append(case)

            if len(case) > 2 and case[2] == False:
                continue

            convertedText = case[0].replace(',', '#').replace('.', ',').replace('#', '.')
            convertedList.append((convertedText, case[1]))

            minusNumber = case[1] * -1 if case[1] is not None else None
            convertedList.append((f'-{case[0]}', minusNumber))
            convertedList.append((f'-{convertedText}', minusNumber))

        return convertedList
