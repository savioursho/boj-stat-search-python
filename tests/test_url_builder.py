from boj_stat_search.url_builder import build_metadata_api_url


def test_build_metadata_api_url_returns_expected_url():
    db = "IR01"

    result = build_metadata_api_url(db)

    assert result == "https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=IR01"
