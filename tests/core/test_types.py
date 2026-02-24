import pytest

from boj_stat_search.core.database import _DB_CATALOG
from boj_stat_search.core.types import Code, Db, Frequency, Period


def test_db_is_str_enum():
    assert Db.FM01 == "FM01"
    assert isinstance(Db.FM01, str)


def test_db_member_count():
    assert len(Db) == 50


def test_db_members_match_catalog():
    catalog_names = {info.name for info in _DB_CATALOG}
    assert {member.value for member in Db} == catalog_names


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


def test_code_accepts_plain_series_code():
    code = Code("MADR1Z@D")

    assert code.db is None
    assert code.codes == ("MADR1Z@D",)
    assert code.to_api_value() == "MADR1Z@D"
    assert str(code) == "MADR1Z@D"


def test_code_accepts_db_code_format():
    code = Code("IR01'MADR1Z@D")

    assert code.db == "IR01"
    assert code.codes == ("MADR1Z@D",)
    assert code.to_api_value() == "MADR1Z@D"


def test_code_accepts_mixed_prefixed_and_plain_values():
    code = Code("IR01'A", "B")

    assert code.db == "IR01"
    assert code.codes == ("A", "B")
    assert code.to_api_value() == "A,B"


def test_code_rejects_conflicting_db_prefixes():
    with pytest.raises(ValueError, match="conflicting DB"):
        Code("IR01'A", "FM01'B")


def test_code_rejects_empty_input():
    with pytest.raises(ValueError, match="between 1 and 250"):
        Code()


def test_code_rejects_too_many_values():
    with pytest.raises(ValueError, match="between 1 and 250"):
        Code(*[f"S{i}" for i in range(251)])


def test_code_rejects_non_string_value():
    with pytest.raises(ValueError, match="must be a string"):
        Code("A", 1)  # type: ignore[arg-type]


def test_code_rejects_empty_string_value():
    with pytest.raises(ValueError, match="non-empty"):
        Code("")


def test_code_rejects_empty_db_prefix_in_db_code_format():
    with pytest.raises(ValueError, match="DB prefix"):
        Code("'ABC")


def test_code_rejects_empty_code_in_db_code_format():
    with pytest.raises(ValueError, match="series code"):
        Code("IR01'")
