from boj_stat_search.core.formatter import format_layer_tree
from boj_stat_search.core.types import Layer
from boj_stat_search.models import MetadataEntry


def show_layers(
    metadata_entries: tuple[MetadataEntry, ...],
    layer: Layer | str | None = None,
) -> None:
    print(format_layer_tree(metadata_entries=metadata_entries, layer=layer))
