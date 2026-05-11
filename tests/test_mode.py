import pytest

from gamedata.mode import Mode, parse_mode


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("week", Mode.WEEK),
        ("W", Mode.WEEK),
        ("w", Mode.WEEK),
        ("month", Mode.MONTH),
        ("M", Mode.MONTH),
        ("m", Mode.MONTH),
        ("quarter", Mode.QUARTER),
        ("q", Mode.QUARTER),
        ("Q", Mode.QUARTER),
        ("cq", Mode.QUARTER),
        ("CQ", Mode.QUARTER),
        ("year", Mode.YEAR),
        ("y", Mode.YEAR),
        ("Y", Mode.YEAR),
        ("cy", Mode.YEAR),
        ("CY", Mode.YEAR),
    ],
)
def test_parse_mode_aliases(value: str, expected: Mode):
    assert parse_mode(value) == expected


@pytest.mark.parametrize("value", ["fiscalyear", "fy", "FY"])
def test_parse_mode_fiscal_year_not_supported(value: str):
    with pytest.raises(NotImplementedError):
        parse_mode(value)


@pytest.mark.parametrize("value", ["fiscalquarter", "fiscalquater", "fq", "FQ"])
def test_parse_mode_fiscal_quarter_not_supported(value: str):
    with pytest.raises(NotImplementedError):
        parse_mode(value)


def test_parse_mode_invalid_value():
    with pytest.raises(ValueError):
        parse_mode("invalid")
