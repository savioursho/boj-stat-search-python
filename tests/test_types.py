import pytest

from boj_stat_search.core.types import Frequency, Period


def test_period_year_constructor_returns_expected_value():
    assert Period.year(2025).to_api_value() == "2025"


def test_period_half_constructor_returns_expected_value():
    assert Period.half(2025, 2).to_api_value() == "202502"


def test_period_quarter_constructor_returns_expected_value():
    assert Period.quarter(2025, 4).to_api_value() == "202504"


def test_period_month_constructor_returns_expected_value():
    assert Period.month(2025, 12).to_api_value() == "202512"


def test_period_to_api_value_accepts_frequency_enum():
    assert Period.quarter(2025, 1).to_api_value(Frequency.QUARTERLY) == "202501"


def test_period_to_api_value_accepts_frequency_string():
    assert Period.month(2025, 9).to_api_value("m") == "202509"


def test_period_to_api_value_rejects_invalid_granularity_for_frequency():
    with pytest.raises(ValueError, match="expected YYYY"):
        Period.month(2025, 1).to_api_value("CY")


def test_period_to_api_value_rejects_invalid_daily_value():
    with pytest.raises(ValueError, match="between 01 and 12"):
        Period.from_string("202500").to_api_value("D")


def test_period_rejects_invalid_year():
    with pytest.raises(ValueError, match="year"):
        Period.year(999)


def test_period_rejects_invalid_half():
    with pytest.raises(ValueError, match="half"):
        Period.half(2025, 3)


def test_period_rejects_invalid_quarter():
    with pytest.raises(ValueError, match="quarter"):
        Period.quarter(2025, 5)


def test_period_rejects_invalid_month():
    with pytest.raises(ValueError, match="month"):
        Period.month(2025, 13)
