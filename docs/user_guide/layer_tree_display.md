# Layer Tree Display

Print metadata hierarchy quickly with `show_layers`.

## Basic Usage

```python
from boj_stat_search import get_metadata, show_layers

metadata = get_metadata(db="BP01")
show_layers(metadata.result_set)
```

`show_layers` prints a formatted layer tree.  
Output includes indentation and layer numbers, for example:

```text
- (1) Deposits
  - (1,1) Domestic banks [XXXX]
```

## Filter by Layer Prefix

Show only one branch:

```python
from boj_stat_search import get_metadata, show_layers

metadata = get_metadata(db="BP01")
show_layers(metadata.result_set, layer="1,1")
```

You can also use wildcard filters:

```python
show_layers(metadata.result_set, layer="1,*,3")
```

## Layer Filter Input

- `layer=None`: print all entries
- `layer="1,1"`: filter by prefix
- `layer="1,*,3"`: wildcard matching

## Top-Level API Used Here

```python
from boj_stat_search import get_metadata, show_layers
```

## Next Step

Return to the [User Guide index](./README.md).
