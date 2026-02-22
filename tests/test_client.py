from unittest.mock import MagicMock, Mock, patch

import httpx

from boj_stat_search import BojClient
from boj_stat_search.models import DataResponse, MetadataResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_metadata_response() -> MetadataResponse:
    return MetadataResponse(
        status=200,
        message_id="M181000I",
        message="ok",
        date="2026-02-21T05:00:12.008+09:00",
        db="IR01",
        result_set=(),
    )


def _make_data_response() -> DataResponse:
    return DataResponse(
        status=200,
        message_id="M181000I",
        message="ok",
        date="2026-02-21T15:58:56.071+09:00",
        parameter={},
        next_position=None,
        result_set=(),
    )


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


def test_context_manager_returns_self():
    with BojClient() as c:
        assert isinstance(c, BojClient)


def test_context_manager_closes_internal_client_on_exit():
    with patch("boj_stat_search.client.httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        with BojClient():
            pass
        mock_instance.close.assert_called_once()


def test_context_manager_delegates_get_metadata():
    expected = _make_metadata_response()
    with patch("boj_stat_search.client.get_metadata", return_value=expected) as mock_fn:
        with BojClient() as c:
            result = c.get_metadata("IR01")
    mock_fn.assert_called_once_with("IR01", "raise", client=c._client)
    assert result is expected


# ---------------------------------------------------------------------------
# Explicit close
# ---------------------------------------------------------------------------


def test_explicit_close_closes_internal_client():
    with patch("boj_stat_search.client.httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        c = BojClient()
        c.close()
        mock_instance.close.assert_called_once()


def test_close_is_idempotent_for_internal_client():
    with patch("boj_stat_search.client.httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        c = BojClient()
        c.close()
        c.close()
        assert mock_instance.close.call_count == 2


# ---------------------------------------------------------------------------
# External client — close is a no-op
# ---------------------------------------------------------------------------


def test_external_client_is_not_closed_on_exit():
    external = Mock(spec=httpx.Client)
    with BojClient(client=external):
        pass
    external.close.assert_not_called()


def test_explicit_close_does_not_close_external_client():
    external = Mock(spec=httpx.Client)
    c = BojClient(client=external)
    c.close()
    external.close.assert_not_called()


def test_external_client_is_used_for_requests():
    external = Mock(spec=httpx.Client)
    expected = _make_metadata_response()
    with patch("boj_stat_search.client.get_metadata", return_value=expected) as mock_fn:
        c = BojClient(client=external)
        result = c.get_metadata("IR01")
    mock_fn.assert_called_once_with("IR01", "raise", client=external)
    assert result is expected


# ---------------------------------------------------------------------------
# Delegation — get_metadata
# ---------------------------------------------------------------------------


def test_get_metadata_delegates_to_functional_api():
    expected = _make_metadata_response()
    with patch("boj_stat_search.client.get_metadata", return_value=expected) as mock_fn:
        c = BojClient()
        result = c.get_metadata("IR01")
    mock_fn.assert_called_once_with("IR01", "raise", client=c._client)
    assert result is expected


# ---------------------------------------------------------------------------
# Delegation — get_data_code
# ---------------------------------------------------------------------------


def test_get_data_code_delegates_minimal_args():
    expected = _make_data_response()
    with patch(
        "boj_stat_search.client.get_data_code", return_value=expected
    ) as mock_fn:
        c = BojClient()
        result = c.get_data_code("FM01", "STRDCLUCON")
    mock_fn.assert_called_once_with(
        "FM01", "STRDCLUCON", None, None, None, "raise", client=c._client
    )
    assert result is expected


def test_get_data_code_delegates_all_optional_args():
    expected = _make_data_response()
    with patch(
        "boj_stat_search.client.get_data_code", return_value=expected
    ) as mock_fn:
        c = BojClient()
        result = c.get_data_code(
            "FM01",
            "STRDCLUCON",
            start_date="202501",
            end_date="202512",
            start_position=10,
        )
    mock_fn.assert_called_once_with(
        "FM01", "STRDCLUCON", "202501", "202512", 10, "raise", client=c._client
    )
    assert result is expected


# ---------------------------------------------------------------------------
# Delegation — get_data_layer
# ---------------------------------------------------------------------------


def test_get_data_layer_delegates_minimal_args():
    expected = _make_data_response()
    with patch(
        "boj_stat_search.client.get_data_layer", return_value=expected
    ) as mock_fn:
        c = BojClient()
        result = c.get_data_layer("MD10", "Q", "*")
    mock_fn.assert_called_once_with(
        "MD10", "Q", "*", None, None, None, "raise", client=c._client
    )
    assert result is expected


def test_get_data_layer_delegates_all_optional_args():
    expected = _make_data_response()
    with patch(
        "boj_stat_search.client.get_data_layer", return_value=expected
    ) as mock_fn:
        c = BojClient()
        result = c.get_data_layer(
            "BP01",
            "M",
            "1,1,1",
            start_date="202504",
            end_date="202509",
            start_position=255,
        )
    mock_fn.assert_called_once_with(
        "BP01", "M", "1,1,1", "202504", "202509", 255, "raise", client=c._client
    )
    assert result is expected


# ---------------------------------------------------------------------------
# Throttling
# ---------------------------------------------------------------------------


def test_throttle_sleeps_when_interval_not_elapsed():
    """Only 0.3 s elapsed; with min_request_interval=1.0 expects ~0.7 s sleep."""
    with patch("boj_stat_search.client.time") as mock_time:
        # First monotonic() → _last_request_time init is 0.0 (not called yet)
        # _throttle: elapsed = monotonic() - 0.0; then sleep; then monotonic() again
        mock_time.monotonic.side_effect = [
            0.3,
            1.0,
        ]  # elapsed=0.3, then post-sleep stamp
        mock_time.sleep = MagicMock()

        c = BojClient(min_request_interval=1.0)
        c._throttle()

        mock_time.sleep.assert_called_once()
        sleep_arg = mock_time.sleep.call_args[0][0]
        assert abs(sleep_arg - 0.7) < 1e-9


def test_throttle_does_not_sleep_when_interval_elapsed():
    """More than 1.0 s elapsed → no sleep."""
    with patch("boj_stat_search.client.time") as mock_time:
        mock_time.monotonic.side_effect = [1.5, 1.5]  # elapsed=1.5, update stamp
        mock_time.sleep = MagicMock()

        c = BojClient(min_request_interval=1.0)
        c._throttle()

        mock_time.sleep.assert_not_called()


def test_throttle_disabled_when_zero():
    """min_request_interval=0 → no sleep regardless of elapsed time."""
    with patch("boj_stat_search.client.time") as mock_time:
        mock_time.sleep = MagicMock()

        c = BojClient(min_request_interval=0)
        c._throttle()

        mock_time.sleep.assert_not_called()
        mock_time.monotonic.assert_not_called()


def test_throttle_updates_last_request_time():
    """After _throttle(), _last_request_time is set to the second monotonic() call."""
    with patch("boj_stat_search.client.time") as mock_time:
        mock_time.monotonic.side_effect = [2.0, 3.5]
        mock_time.sleep = MagicMock()

        c = BojClient(min_request_interval=1.0)
        c._throttle()

        assert c._last_request_time == 3.5


def test_throttle_applied_to_all_methods():
    """_throttle is called once per API method invocation."""
    meta = _make_metadata_response()
    data = _make_data_response()

    with (
        patch("boj_stat_search.client.get_metadata", return_value=meta),
        patch("boj_stat_search.client.get_data_code", return_value=data),
        patch("boj_stat_search.client.get_data_layer", return_value=data),
    ):
        c = BojClient(min_request_interval=0)  # disable real sleeping
        with patch.object(c, "_throttle") as mock_throttle:
            c.get_metadata("IR01")
            c.get_data_code("FM01", "CODE")
            c.get_data_layer("MD10", "Q", "*")

        assert mock_throttle.call_count == 3


# ---------------------------------------------------------------------------
# on_validation_error propagation
# ---------------------------------------------------------------------------


def test_on_validation_error_default_is_raise():
    c = BojClient()
    assert c.on_validation_error == "raise"


def test_on_validation_error_forwarded_to_get_metadata():
    expected = _make_metadata_response()
    with patch("boj_stat_search.client.get_metadata", return_value=expected) as mock_fn:
        c = BojClient(on_validation_error="warn")
        c.get_metadata("IR01")
    mock_fn.assert_called_once_with("IR01", "warn", client=c._client)


def test_on_validation_error_forwarded_to_get_data_code():
    expected = _make_data_response()
    with patch(
        "boj_stat_search.client.get_data_code", return_value=expected
    ) as mock_fn:
        c = BojClient(on_validation_error="ignore")
        c.get_data_code("FM01", "STRDCLUCON")
    mock_fn.assert_called_once_with(
        "FM01", "STRDCLUCON", None, None, None, "ignore", client=c._client
    )


def test_on_validation_error_forwarded_to_get_data_layer():
    expected = _make_data_response()
    with patch(
        "boj_stat_search.client.get_data_layer", return_value=expected
    ) as mock_fn:
        c = BojClient(on_validation_error="warn")
        c.get_data_layer("MD10", "Q", "*")
    mock_fn.assert_called_once_with(
        "MD10", "Q", "*", None, None, None, "warn", client=c._client
    )
