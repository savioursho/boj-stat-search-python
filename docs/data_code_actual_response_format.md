# Data Code API Actual Response Format

This document describes the **actual** JSON response format observed from live calls to:

- `https://www.stat-search.boj.or.jp/api/v1/getDataCode`

Observed on **2026-02-21 (JST)** using:

- `get_data_code_raw(db="FM01", code="STRDCLUCON")`
- `GET /api/v1/getDataCode?lang=en&db=FM01&code=STRDCLUCON`

## Top-Level Shape

```json
{
  "STATUS": 200,
  "MESSAGEID": "M181000I",
  "MESSAGE": "正常に終了しました。",
  "DATE": "2026-02-21T15:58:56.071+09:00",
  "PARAMETER": {
    "FORMAT": "",
    "LANG": "",
    "DB": "FM01",
    "STARTDATE": "",
    "ENDDATE": "",
    "STARTPOSITION": ""
  },
  "NEXTPOSITION": null,
  "RESULTSET": [
    {
      "SERIES_CODE": "STRDCLUCON",
      "NAME_OF_TIME_SERIES_J": "無担保コールＯ／Ｎ物レート／平均値 日次／金利",
      "UNIT_J": "年％",
      "FREQUENCY": "DAILY",
      "CATEGORY_J": "コールレート",
      "LAST_UPDATE": 20260220,
      "VALUES": {
        "SURVEY_DATES": [19980105, 19980106],
        "VALUES": [0.49, 0.49]
      }
    }
  ]
}
```

## Top-Level Field Types

| Field | Type | Notes |
| --- | --- | --- |
| `STATUS` | `int` | HTTP-like result code in payload. |
| `MESSAGEID` | `str` | BOJ message code. |
| `MESSAGE` | `str` | Human-readable message (JP/EN depends on request). |
| `DATE` | `str` | Timestamp string with timezone offset. |
| `PARAMETER` | `dict[str, str]` | Echo of request parameters (see below). |
| `NEXTPOSITION` | `int \| null` | Pagination continuation point. |
| `RESULTSET` | `list[object]` | Data entries for requested series code(s). |

## `PARAMETER` Object

Observed keys:

- `FORMAT`
- `LANG`
- `DB`
- `STARTDATE`
- `ENDDATE`
- `STARTPOSITION`

Notes:

- Values are strings.
- Omitted optional params are returned as empty strings.
- `STARTPOSITION` is a string (for example `""`), not a number.
- `CODE` was **not** present in `PARAMETER` in observed responses.

## `RESULTSET` Entry Shape

Shared keys:

- `SERIES_CODE` (`str`)
- `FREQUENCY` (`str`)
- `LAST_UPDATE` (`int`, `YYYYMMDD`)
- `VALUES` (`object`)

Language-dependent keys:

- JP/default: `NAME_OF_TIME_SERIES_J`, `UNIT_J`, `CATEGORY_J`
- EN: `NAME_OF_TIME_SERIES`, `UNIT`, `CATEGORY`

## `VALUES` Object

`VALUES` has the following shape:

```json
{
  "SURVEY_DATES": [19980105, 19980106, 19980107],
  "VALUES": [0.49, 0.49, null]
}
```

Notes:

- `SURVEY_DATES` elements are integers.
- `VALUES` elements are numbers or `null`.
- `SURVEY_DATES` and `VALUES` align positionally (same index = same observation).
