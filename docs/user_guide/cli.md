# Command-Line Interface

Query BOJ statistics directly from the terminal.

## Overview

After installation, the `boj-stat-search` command is available. It provides six subcommands:

| Command | Description |
|---------|-------------|
| `list-db` | List all available databases |
| `get-metadata` | Get metadata for a database (JSON) |
| `show-layers` | Show the layer structure of a database |
| `get-data-code` | Get data by series code (JSON) |
| `get-data-layer` | Get data by layer and frequency (JSON) |
| `generate-metadata-parquet` | Generate per-DB metadata Parquet files under a local directory |

Run `boj-stat-search --help` to see all commands, or `boj-stat-search <command> --help` for command-specific help.

## List Databases

```bash
boj-stat-search list-db
```

Prints a table of all databases with name, category, and description:

```text
FM01  Financial Markets  Uncollateralized Overnight Call Rate (average) (Updated every business day)
FM02  Financial Markets  Short-term Money Market Rates
...
```

## Get Metadata

```bash
boj-stat-search get-metadata FM01
```

Prints the full metadata response as JSON. Pipe to `jq` for filtering:

```bash
boj-stat-search get-metadata FM01 | jq '.result_set[0].series_code'
```

## Show Layers

```bash
boj-stat-search show-layers FM01
```

Prints a formatted layer tree (same output as `show_layers` in Python).

Filter to a specific layer with `--layer`:

```bash
boj-stat-search show-layers BP01 --layer 1,1
```

## Get Data by Series Code

```bash
boj-stat-search get-data-code FM01 STRDCLUCON
```

Prints data as JSON. Optional date and pagination filters:

```bash
boj-stat-search get-data-code FM01 STRDCLUCON \
    --start-date 202401 \
    --end-date 202401
```

Series codes can be found in metadata output (the `series_code` field) or in the layer tree (shown in brackets).

The date format depends on the series frequency — see [Date Format Rules](../api_manual/request_basics.md#date-format-rules) for details. For daily, weekly, and monthly series, use `YYYYMM`.

| Option | Short | Description |
|--------|-------|-------------|
| `--start-date` | `-s` | Start date (format depends on frequency) |
| `--end-date` | `-e` | End date (format depends on frequency) |
| `--start-position` | `-p` | Start position for pagination |

## Get Data by Layer

```bash
boj-stat-search get-data-layer BP01 M "1,1,1"
```

Arguments are database code, frequency, and layer specification. The same date and pagination options are available:

```bash
boj-stat-search get-data-layer BP01 M "1,1,1" \
    --start-date 202504 \
    --end-date 202509
```

## Error Handling

When the BOJ API returns an error, the CLI prints a message to stderr and exits with code 1:

```text
API error: HTTP 400 BOJ API error, status=400, message_id=M181015E, message=...
```

Validation errors (e.g. forbidden characters in the code) are raised before the request is sent and also exit with a non-zero code.

## JSON Output

`get-metadata`, `get-data-code`, and `get-data-layer` output JSON to stdout. This makes them composable with standard Unix tools:

```bash
# Pretty-print with jq
boj-stat-search get-metadata FM01 | jq .

# Save to file
boj-stat-search get-data-code FM01 STRDCLUCON > data.json

# Extract specific fields
boj-stat-search get-data-layer BP01 M "1,1,1" | jq '.result_set[].SERIES_CODE'
```

## Generate Metadata Parquet Files

```bash
boj-stat-search generate-metadata-parquet
```

Fetches metadata for all known DBs and writes one file per DB under `metadata/`:
The command shows a live `tqdm` progress bar while DBs are being processed.

```text
metadata/FM01.parquet
metadata/BP01.parquet
...
```

Select specific DBs with repeatable `--db` options:

```bash
boj-stat-search generate-metadata-parquet --db FM01 --db BP01
```

Write to a custom directory:

```bash
boj-stat-search generate-metadata-parquet --output-dir ./tmp/metadata
```

Control request pacing (seconds between calls):

```bash
boj-stat-search generate-metadata-parquet --min-request-interval 0.5
```

If one or more DB requests fail, the command continues processing remaining DBs, prints failures, and exits with code 1.

## Next Step

Return to the [User Guide index](./README.md).
