from boj_stat_search.shell.display import show_layers
from boj_stat_search.core.models import MetadataEntry


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


def test_show_layers_prints_formatted_tree(capsys):
    entries = (
        _entry(name_of_time_series="Root", layer1=1),
        _entry(series_code="S1", name_of_time_series="First", layer1=1, layer2=1),
    )

    show_layers(entries)

    captured = capsys.readouterr()
    assert captured.out == "- (1) Root\n  - (1,1) First [S1]\n"
    assert captured.err == ""


def test_show_layers_prints_filtered_tree(capsys):
    entries = (
        _entry(series_code="A", name_of_time_series="A", layer1=1, layer2=1),
        _entry(series_code="B", name_of_time_series="B", layer1=2, layer2=1),
    )

    show_layers(entries, layer="1")

    captured = capsys.readouterr()
    assert captured.out == "  - (1,1) A [A]\n"
    assert captured.err == ""
