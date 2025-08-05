from parameterized import parameterized

from Service.Conversion.AbstractConversionManagerTest import AbstractConversionManagerTest
from src.Service.Conversion.Unit.UnitParser import UnitParser


class TestUnitParser(AbstractConversionManagerTest):
    @parameterized.expand([
        ('Simple', '5ft', 5, 'ft'),
        ('With whitespace, uppercase', ' 5 FT ', 5, 'ft'),
        ('Fractional', '5.5kg', 5.5, 'kg'),
        ('Special symbols ft', '18\'', 18, '\''),
        ('Special symbols in', '18"', 18, '"'),
        ('Special symbols BTC', '₿0.155', 0.155, '₿'),
        ('Unit with number', '3m3', 3, 'm3'),
        ('Thousands separator 1', '1,234,567m', 1234567, 'm'),
        ('Thousands separator 2', '1.234.567m', 1234567, 'm'),
        ('Thousands separator 3', '1 2 3 4 m', 1234, 'm'),
        ('Thousands separator 4', '1 2 3 4 , 1m', 1234.1, 'm'),

        # Compound units like 5'11" generally are not supported. But current parsers
        # already half-parse them, treating as 5ft (cutting off inches).
        # So we test to ensure this compatibility remains
        ('Compound ft in', '18′5″', 18, '′'),

        # Should not be matched
        ('Not existing unit', '5ab'),
        ('Thousands separator invalid', '1,234.567,890m'),
        ('Invalid 1', '5'),
        ('Invalid 2', '5.5'),
        ('Invalid 3', 'a'),
        ('Invalid 4', '-'),
        ('Invalid 5', ' '),
        ('Invalid 6', '3 3'),
        ('Invalid 7', 'm3m'),
    ])
    def testParseText(
        self, _: str,
        text: str,
        expectNumber: float | None = None, expectUnit: str | None = None,
    ) -> None:
        services = self.setupServices()
        parser = services[UnitParser]

        result = parser.parseText(text)

        if expectNumber is None:
            self.assertEqual(None, result)
        else:
            self.assertEqual(expectNumber, result.number)  # type: ignore[union-attr]
            self.assertEqual(expectUnit, result.unit)  # type: ignore[union-attr]
