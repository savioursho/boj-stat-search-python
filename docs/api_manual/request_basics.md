# Request Basics

How to call the original BOJ Stat-Search Web API.

## Base URL and Endpoints

- Base: `https://www.stat-search.boj.or.jp/api/v1`
- Metadata API: `/getMetadata`
- Data Code API: `/getDataCode`
- Data Layer API: `/getDataLayer`

## Core Query Parameters

Common parameters:

- `db`: database name (required for all endpoints)
- `format`: `json` or `csv` (optional)
- `lang`: `jp` or `en` (optional)

Endpoint-specific parameters:

- `getDataCode`:
  - `code` (required): comma-separated series codes
  - `startDate`, `endDate` (optional)
  - `startPosition` (optional, integer >= 1)
- `getDataLayer`:
  - `frequency` (required): `CY`, `FY`, `CH`, `FH`, `Q`, `M`, `W`, `D`
  - `layer` (required): `*` or comma-separated layer values (1 to 5 levels)
  - `startDate`, `endDate` (optional)
  - `startPosition` (optional, integer >= 1)

> Note for `boj_stat_search` users: this page documents the raw BOJ API, where `db` is required.
> The Python wrapper adds optional conveniences for `get_data_code` (for example `Code("DB'CODE")` input and cache-based DB resolution when `db` is omitted).
> See [User Guide: Querying Data](../user_guide/querying_data.md).

## Date Format Rules

From the official manual:

- `CY`, `FY`: `YYYY`
- `CH`, `FH`: `YYYYHH` (`HH` is `01` or `02`)
- `Q`: `YYYYQQ` (`QQ` is `01` to `04`)
- `M`, `W`, `D`: `YYYYMM` for request parameters

## Request Examples

Metadata:

```text
https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=FM01&format=json&lang=en
```

Data code:

```text
https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON&format=json&lang=en
```

Data layer:

```text
https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*&format=json&lang=en&startPosition=1
```

## Defaults When Omitted

When `format` and `lang` are omitted, observed responses on February 21, 2026 were:

- JSON format response body
- Japanese message text and JP-oriented output fields

Example:

```text
https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON
```

## Operational Notes

- The manual states parameter names and values are case-insensitive.
- The service warns against high-frequency access.
