from boj_stat_search.core.request_planner import pick_first_code_for_db_resolution
from boj_stat_search.core.types import Code, Db


def test_returns_none_when_db_provided():
    result = pick_first_code_for_db_resolution(db="FM01", code="STRDCLUCON")
    assert result is None


def test_returns_none_when_db_enum_provided():
    result = pick_first_code_for_db_resolution(db=Db.FM01, code="STRDCLUCON")
    assert result is None


def test_returns_none_when_code_has_embedded_db():
    code = Code("FM01'STRDCLUCON")
    result = pick_first_code_for_db_resolution(db=None, code=code)
    assert result is None


def test_returns_code_for_simple_string():
    result = pick_first_code_for_db_resolution(db=None, code="STRDCLUCON")
    assert result == "STRDCLUCON"


def test_returns_first_code_for_comma_separated():
    result = pick_first_code_for_db_resolution(db=None, code="STRDCLUCON,STRACLUCON")
    assert result == "STRDCLUCON"


def test_returns_none_for_none_code():
    result = pick_first_code_for_db_resolution(db=None, code=None)
    assert result is None


def test_returns_none_for_empty_string():
    result = pick_first_code_for_db_resolution(db=None, code="")
    assert result is None


def test_returns_code_value_for_code_object_without_db():
    code = Code("STRDCLUCON")
    result = pick_first_code_for_db_resolution(db=None, code=code)
    assert result == "STRDCLUCON"


def test_returns_first_code_value_for_multi_code_object_without_db():
    code = Code("STRDCLUCON", "STRACLUCON")
    result = pick_first_code_for_db_resolution(db=None, code=code)
    assert result == "STRDCLUCON"
