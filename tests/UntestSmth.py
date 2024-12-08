import time
from unittest import TestCase
from unittest.mock import Mock

from src.Service.Conversion.Converter.SimpleUnit.SimpleUnitConverter import SimpleUnitConverter


# TODO next: tests
class TestSmth(TestCase):
    # TODO add tests for other classes as well
    # unit tests for SimpleUnitConverter:
    # .py and other not-numbers
    # Functional test for the entire conversion framework, testing all converters loading and other common cases

    # TODO unit tests:
    # 59C
    # 0°F
    # 1Fahrenheit
    # -5°Fahrenheit
    # 3000*Fahrenheit
    # 60mph
    # 102.5kmh
    # 103,6mm
    # 1,2.3,4.5wtf
    # 15m/s
    # 1-1invalid
    # [whitespace trimming]
    # [very big numbers]
    # [uppercase/lowercase]
    # [loooong numbers: 12345679123456789c or 1.2345679123456789c]

    _dataProvider = [
        ('100',           100),
        ('10,5',          10.5),
        ('10.5',          10.5),
        ('10,50',         10.5),
        ('10.50',         10.5),
        ('56,123',        56123),
        ('56.123',        56123),
        ('100.500',       100500), # triple digit before/after separator - can be both
        ('100,500',       100500), # But if it's 100, why would someone write it as 100.000? So 100k probably makes more sense
        ('100.5000',      100.5),
        ('100,5000',      100.5),
        ('1,123,456',     1123456),
        ('1.123.456',     1123456),
        ('1,123,456.789', 1123456.789),
        ('1.123.456,789', 1123456.789),
        ('1,123.456.789', None),
        ('1.123,456,789', None),
        ('1,2,3',         None),
        ('1.2.3',         None),
        ('11,22,33',      None),
        ('11.22.33',      None),
        ('11,222,33',     None),
        ('11.222.33',     None),
        ('11,222,333',    11222333),
        ('11.222.333',    11222333),
        ('1234,4567.789', None),
        ('1234.4567,789', None),


        ('001', 1),
        ('1,,5', None),
        ('1..5', None),
        ('1.,5', None),
        ('1,.5', None),
        (',', None),
        ('.', None),
    ]

    def testCorrectness(self):
        converter = SimpleUnitConverter(Mock())
        correct = 0
        total = 0

        print('%12s => %12s  != %12s' % ('From', 'Expected', 'Error'))

        for testCase in self._dataProvider:
            total += 1
            result, x = converter._parseNumber1_SORegex(testCase[0])

            print('%12s => %12s' % (testCase[0], testCase[1]), end='')

            if result != testCase[1]:
                print('  != %12s' % result)
            else:
                correct += 1
                print()

        print(f'Correct: {correct}/{total}')

        # TODO assert here that all tests passed





    def testPerformance(self):
        converter = SimpleUnitConverter(Mock())

        # loops = 1_000_000
        loops = 0
        start = time.time()

        for i in range(loops):
            # result = converter._parseNumber('1,123,456.789')
            # Completed 50 000 000 loops in 4.42292857170105 s

            result = converter._parseNumber1_SORegex('1,123,456.789')
            # Completed 1 000 000 loops in 2.318953275680542 s
            # Completed 5 000 000 loops in 12.577008724212646 s

            # result = converter._parseNumber2_GPT_SimpleStupid('1,123,456.789')
            # Completed 1 000 000 loops in 0.4923388957977295 s
            # Completed 5 000 000 loops in 2.3958756923675537 s

            # result = converter._parseNumber3_GPT_Advanced('1,123,456.789')
            # Completed 1 000 000 loops in 1.4284043312072754 s

        end = time.time()

        print(f'Completed {loops} loops in {end - start} s')

        # print(result)
        self.assertEqual(1, 1)
