from boj_stat_search.models import DbInfo


_DB_CATALOG: tuple[DbInfo, ...] = (
    DbInfo(
        name="IRO1",
        desc="The Basic Discount Rates and Basic Loan Rates (Previously Indicated as \"Official Discount Rates\")",
        category="Interest Rates on Deposits and Loans",
    ),
)

def list_db() -> tuple[DbInfo, ...]:
    """List all available databases."""
    return _DB_CATALOG
