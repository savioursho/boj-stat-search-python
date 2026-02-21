import pytest

from boj_stat_search.core import format_layer_tree
from boj_stat_search.core.types import Layer
from boj_stat_search.models import MetadataEntry


def _entry(
    *,
    series_code: str = "",
    name_of_time_series: str = "",
    name_of_time_series_j: str = "",
    layer1: int = 0,
    layer2: int = 0,
    layer3: int = 0,
    layer4: int = 0,
    layer5: int = 0,
) -> MetadataEntry:
    return MetadataEntry(
        series_code=series_code,
        name_of_time_series_j=name_of_time_series_j,
        name_of_time_series=name_of_time_series,
        unit_j="",
        unit="",
        frequency="",
        category_j="",
        category="",
        layer1=layer1,
        layer2=layer2,
        layer3=layer3,
        layer4=layer4,
        layer5=layer5,
        start_of_the_time_series="",
        end_of_the_time_series="",
        last_update="",
        notes_j="",
        notes="",
    )


def test_format_layer_tree_formats_entries_in_sorted_tree_order():
    entries = (
        _entry(series_code="S2", name_of_time_series="Second", layer1=1, layer2=2),
        _entry(name_of_time_series="Root", layer1=1),
        _entry(series_code="S1", name_of_time_series="First", layer1=1, layer2=1),
        _entry(name_of_time_series="Root2", layer1=2),
    )

    result = format_layer_tree(entries)

    assert result == "\n".join(
        [
            "- (1) Root",
            "  - (1,1) First [S1]",
            "  - (1,2) Second [S2]",
            "- (2) Root2",
        ]
    )


def test_format_layer_tree_uses_label_fallbacks():
    entries = (
        _entry(series_code="A1", name_of_time_series="EN label", layer1=1, layer2=1),
        _entry(series_code="A2", name_of_time_series_j="JP label", layer1=1, layer2=2),
        _entry(series_code="A3", layer1=1, layer2=3),
        _entry(layer1=1, layer2=4),
    )

    result = format_layer_tree(entries)

    assert result == "\n".join(
        [
            "  - (1,1) EN label [A1]",
            "  - (1,2) JP label [A2]",
            "  - (1,3) A3 [A3]",
            "  - (1,4) (unnamed)",
        ]
    )


def test_format_layer_tree_filters_by_layer_prefix():
    entries = (
        _entry(series_code="A", name_of_time_series="A", layer1=1, layer2=1),
        _entry(series_code="B", name_of_time_series="B", layer1=1, layer2=1, layer3=1),
        _entry(series_code="C", name_of_time_series="C", layer1=1, layer2=2),
        _entry(series_code="D", name_of_time_series="D", layer1=2, layer2=1),
    )

    result = format_layer_tree(entries, layer=Layer(1, 1))

    assert result == "\n".join(
        [
            "  - (1,1) A [A]",
            "    - (1,1,1) B [B]",
        ]
    )


def test_format_layer_tree_filters_by_wildcard_layer_string():
    entries = (
        _entry(series_code="A", name_of_time_series="A", layer1=1, layer2=2, layer3=3),
        _entry(series_code="B", name_of_time_series="B", layer1=1, layer2=9, layer3=3),
        _entry(series_code="C", name_of_time_series="C", layer1=1, layer2=9, layer3=4),
    )

    result = format_layer_tree(entries, layer="1,*,3")

    assert result == "\n".join(
        [
            "    - (1,2,3) A [A]",
            "    - (1,9,3) B [B]",
        ]
    )


def test_format_layer_tree_with_star_filter_matches_all_first_level_branches():
    entries = (
        _entry(name_of_time_series="Root1", layer1=1),
        _entry(name_of_time_series="Root2", layer1=2),
    )

    assert format_layer_tree(entries, layer="*") == format_layer_tree(entries)


def test_format_layer_tree_rejects_empty_layer_filter_string():
    entries = (_entry(name_of_time_series="Root", layer1=1),)

    with pytest.raises(ValueError, match="layer filter"):
        format_layer_tree(entries, layer=" ")


def test_format_layer_tree_rejects_invalid_layer_filter_token():
    entries = (_entry(name_of_time_series="Root", layer1=1),)

    with pytest.raises(ValueError, match="layer filter"):
        format_layer_tree(entries, layer="1,a")


def test_format_layer_tree_returns_empty_string_when_no_entry_matches_filter():
    entries = (
        _entry(series_code="A", name_of_time_series="A", layer1=1, layer2=1),
    )

    assert format_layer_tree(entries, layer=Layer(2)) == ""
