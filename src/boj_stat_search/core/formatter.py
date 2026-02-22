from boj_stat_search.core.types import Layer
from boj_stat_search.models import MetadataEntry


_MAX_LAYER_DEPTH = 5


def _entry_layer_path(entry: MetadataEntry) -> tuple[str, ...]:
    values = (
        entry.layer1,
        entry.layer2,
        entry.layer3,
        entry.layer4,
        entry.layer5,
    )

    path: list[str] = []
    for value in values:
        if value == 0:
            break
        path.append(str(value))
    return tuple(path)


def _choose_label(entry: MetadataEntry) -> str:
    if entry.name_of_time_series != "":
        return entry.name_of_time_series
    if entry.name_of_time_series_j != "":
        return entry.name_of_time_series_j
    if entry.series_code != "":
        return entry.series_code
    return "(unnamed)"


def _parse_layer_filter(layer: Layer | str | None) -> tuple[str, ...] | None:
    if layer is None:
        return None
    if isinstance(layer, Layer):
        return layer.levels
    if not isinstance(layer, str):
        raise ValueError("layer filter: must be Layer, string, or None")

    raw = layer.strip()
    if raw == "":
        raise ValueError("layer filter: must not be empty")

    tokens = [token.strip() for token in raw.split(",")]
    if len(tokens) < 1 or len(tokens) > _MAX_LAYER_DEPTH:
        raise ValueError(
            "layer filter: must have between 1 and 5 comma-separated values"
        )
    if any(token == "" for token in tokens):
        raise ValueError("layer filter: must not contain empty values")
    if any(token != "*" and not token.isdigit() for token in tokens):
        raise ValueError("layer filter: each value must be '*' or digits only")

    return tuple(tokens)


def _matches_layer_filter(
    path: tuple[str, ...],
    layer_filter: tuple[str, ...] | None,
) -> bool:
    if layer_filter is None:
        return True
    if len(layer_filter) > len(path):
        return False

    for idx, filter_token in enumerate(layer_filter):
        if filter_token == "*":
            continue
        if path[idx] != filter_token:
            return False
    return True


def _format_path(path: tuple[str, ...]) -> str:
    if not path:
        return "0"
    return ",".join(path)


def format_layer_tree(
    metadata_entries: tuple[MetadataEntry, ...],
    layer: Layer | str | None = None,
) -> str:
    layer_filter = _parse_layer_filter(layer)

    sorted_entries = sorted(
        metadata_entries,
        key=lambda entry: (
            entry.layer1,
            entry.layer2,
            entry.layer3,
            entry.layer4,
            entry.layer5,
            entry.series_code,
            _choose_label(entry),
        ),
    )

    lines: list[str] = []
    for entry in sorted_entries:
        path = _entry_layer_path(entry)
        if not _matches_layer_filter(path, layer_filter):
            continue

        label = _choose_label(entry)
        if entry.series_code != "":
            text = f"{label} [{entry.series_code}]"
        else:
            text = label

        indent = "  " * max(len(path) - 1, 0)
        lines.append(f"{indent}- ({_format_path(path)}) {text}")

    return "\n".join(lines)
