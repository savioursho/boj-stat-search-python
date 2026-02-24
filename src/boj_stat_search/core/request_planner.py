from boj_stat_search.core.types import Code, Db
from boj_stat_search.core.validator import coerce_code, extract_db_from_code


def pick_first_code_for_db_resolution(db: Db | str | None, code: Code | str | None) -> str | None:
    """Return the first series code to use for DB auto-resolution, or None if not needed."""
    if db is not None:
        return None
    if extract_db_from_code(code) is not None:
        return None
    normalized_code = coerce_code(code)
    if not isinstance(normalized_code, str):
        return None
    first_code = normalized_code.split(",", 1)[0].strip()
    return first_code if first_code else None
