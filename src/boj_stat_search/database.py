from boj_stat_search.models import DbInfo


_DB_CATALOG: tuple[DbInfo, ...] = (
    DbInfo(
        name="IR01",
        desc="The Basic Discount Rates and Basic Loan Rates (Previously Indicated as \"Official Discount Rates\")",
        category="Interest Rates on Deposits and Loans",
    ),
    DbInfo(
        name="IR02",
        desc="Average Interest Rates Posted at Financial Institutions by Type of Deposit",
        category="Interest Rates on Deposits and Loans",
    ),
    DbInfo(
        name="IR03",
        desc="Average Interest Rates on Time Deposits by Term",
        category="Interest Rates on Deposits and Loans",
    ),
    DbInfo(
        name="IR04",
        desc="Average Contract Interest Rates on Loans and Discounts",
        category="Interest Rates on Deposits and Loans",
    ),
    DbInfo(
        name="FM01",
        desc="Uncollateralized Overnight Call Rate (average) (Updated every business day)",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM02",
        desc="Short-term Money Market Rates",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM03",
        desc="Amounts Outstanding in Short-term Money Market",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM04",
        desc="Amounts Outstanding in the Call Money Market",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM05",
        desc="Issuance, Redemption, and Outstanding of Public and Corporate Bonds",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM06",
        desc="Trading of Interest-bearing Government Bonds by Purchaser (Interest-bearing Government Bonds)",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM07",
        desc="(Reference)Government Bonds Sales Over the Counter / Counter Sales Ratio (through January 2004)",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM08",
        desc="Foreign Exchange Rates",
        category="Financial Markets",
    ),
    DbInfo(
        name="FM09",
        desc="Effective Exchange Rate",
        category="Financial Markets",
    ),
    DbInfo(
        name="PS01",
        desc="Other Payment and Settlement Systems",
        category="Payment and Settlement",
    ),
    DbInfo(
        name="PS02",
        desc="Basic Figures on Fails",
        category="Payment and Settlement",
    ),
    DbInfo(
        name="MD01",
        desc="Monetary Base",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD02",
        desc="Money Stock",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD03",
        desc="Monetary Survey",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD04",
        desc="(Reference) Changes in Money Stock (M2+CDs) and Credit",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD05",
        desc="Currency in Circulation",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD06",
        desc="Sources of Changes in Current Account Balances at the Bank of Japan and Market Operations (Final Figures)",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD07",
        desc="Reserves",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD08",
        desc="BOJ Current Account Balances by Sector",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD09",
        desc="Monetary Base and the Bank of Japan's Transactions",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD10",
        desc="Amounts Outstanding of Deposits by Depositor",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD11",
        desc="Deposits, Vault Cash, and Loans and Bills Discounted",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD12",
        desc="Deposits, Vault Cash, and Loans and Bills Discounted by Prefecture (Domestically Licensed Banks)",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD13",
        desc="Principal Figures of Financial Institutions",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="MD14",
        desc="Time Deposits: Amounts Outstanding and New Deposits by Maturity",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="LA01",
        desc="Loans and Bills Discounted by Sector",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="LA02",
        desc="Loans and Discounts by the Bank of Japan",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="LA03",
        desc="Outstanding of Loans (Others)",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="LA04",
        desc="Commitment Lines Extended by Japanese Banks",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="LA05",
        desc="Senior Loan Officer Opinion Survey on Bank Lending Practices at Large Japanese Banks",
        category="Money, Deposits and Loans",
    ),
    DbInfo(
        name="BS01",
        desc="Bank of Japan Accounts",
        category="Balance Sheets of the Bank of Japan and Financial Institutions",
    ),
    DbInfo(
        name="BS02",
        desc="Financial Institutions Accounts",
        category="Balance Sheets of the Bank of Japan and Financial Institutions",
    ),
    DbInfo(
        name="FF",
        desc="Flow of Funds",
        category="Flow of Funds",
    ),
    DbInfo(
        name="OB01",
        desc="Bank of Japan's Transactions with the Government",
        category="Other Bank of Japan Statistics",
    ),
    DbInfo(
        name="OB02",
        desc="Collateral Accepted by the Bank of Japan",
        category="Other Bank of Japan Statistics",
    ),
    DbInfo(
        name="CO",
        desc="TANKAN",
        category="TANKAN",
    ),
    DbInfo(
        name="PR01",
        desc="Corporate Goods Price Index (CGPI)",
        category="Prices",
    ),
    DbInfo(
        name="PR02",
        desc="Services Producer Price Index (SPPI)",
        category="Prices",
    ),
    DbInfo(
        name="PR03",
        desc="Input-Output Price Index of the Manufacturing Industry by Sector (IOPI)",
        category="Prices",
    ),
    DbInfo(
        name="PR04",
        desc="<Satellite series> Final Demand-Intermediate Demand price indexes (FD-ID price indexes)",
        category="Prices",
    ),
    DbInfo(
        name="PF01",
        desc="Statement of Receipts and Payments of the Treasury Accounts",
        category="Public Finance",
    ),
    DbInfo(
        name="PF02",
        desc="National Government Debt",
        category="Public Finance",
    ),
    DbInfo(
        name="BP01",
        desc="Balance of Payments",
        category="Balance of Payments and BIS-Related Statistics",
    ),
    DbInfo(
        name="BIS",
        desc="BIS International Locational Banking Statistics and BIS International Consolidated Banking Statistics in Japan",
        category="Balance of Payments and BIS-Related Statistics",
    ),
    DbInfo(
        name="DER",
        desc="Regular Derivatives Market Statistics in Japan",
        category="Balance of Payments and BIS-Related Statistics",
    ),
    DbInfo(
        name="OT",
        desc="Others",
        category="Others",
    ),
)


def list_db() -> tuple[DbInfo, ...]:
    """List all available databases."""
    return _DB_CATALOG
