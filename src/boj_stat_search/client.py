import httpx

from boj_stat_search.api.api_request import get_data_code, get_data_layer, get_metadata
from boj_stat_search.core.types import ErrorMode, Frequency, Layer, Period
from boj_stat_search.models import DataResponse, MetadataResponse


class BojClient:
    """Stateful client that reuses a single httpx.Client across requests."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        on_validation_error: ErrorMode = "raise",
    ) -> None:
        self._external_client = client is not None
        self._client = client if client is not None else httpx.Client()
        self.on_validation_error = on_validation_error

    # --- context manager ---

    def __enter__(self) -> "BojClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying httpx.Client (no-op if client was supplied externally)."""
        if not self._external_client:
            self._client.close()

    # --- API methods ---

    def get_metadata(self, db: str) -> MetadataResponse:
        return get_metadata(db, self.on_validation_error, client=self._client)

    def get_data_code(
        self,
        db: str,
        code: str,
        start_date: Period | str | None = None,
        end_date: Period | str | None = None,
        start_position: int | None = None,
    ) -> DataResponse:
        return get_data_code(
            db,
            code,
            start_date,
            end_date,
            start_position,
            self.on_validation_error,
            client=self._client,
        )

    def get_data_layer(
        self,
        db: str,
        frequency: Frequency | str,
        layer: Layer | str,
        start_date: Period | str | None = None,
        end_date: Period | str | None = None,
        start_position: int | None = None,
    ) -> DataResponse:
        return get_data_layer(
            db,
            frequency,
            layer,
            start_date,
            end_date,
            start_position,
            self.on_validation_error,
            client=self._client,
        )
