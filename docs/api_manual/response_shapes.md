# Response Shapes

Observed JSON response structures for the original BOJ Web API.

## Common Top-Level Fields

All three endpoints return these top-level keys:

- `STATUS` (integer-like)
- `MESSAGEID` (string)
- `MESSAGE` (string)
- `DATE` (timestamp string, JST)

## Metadata API (`getMetadata`)

Observed top-level keys:

- `STATUS`, `MESSAGEID`, `MESSAGE`, `DATE`, `DB`, `RESULTSET`

Observed success example (trimmed):

```json
{
  "STATUS": 200,
  "MESSAGEID": "M181000I",
  "MESSAGE": "Successfully completed",
  "DATE": "2026-02-21T5:00:11.476+09:00",
  "DB": "FM01",
  "RESULTSET": [
    {
      "SERIES_CODE": "",
      "NAME_OF_TIME_SERIES": "Uncollateralized Overnight Call Rate (Updated every business day)",
      "LAYER1": 1,
      "LAYER2": 0
    }
  ]
}
```

## Data Code API (`getDataCode`)

Observed top-level keys:

- `STATUS`, `MESSAGEID`, `MESSAGE`, `DATE`, `PARAMETER`, `NEXTPOSITION`, `RESULTSET`

Observed success example (trimmed):

```json
{
  "STATUS": 200,
  "MESSAGEID": "M181000I",
  "MESSAGE": "Successfully completed",
  "DATE": "2026-02-21T23:41:54.410+09:00",
  "PARAMETER": {
    "FORMAT": "JSON",
    "LANG": "EN",
    "DB": "FM01",
    "STARTDATE": "",
    "ENDDATE": "",
    "STARTPOSITION": ""
  },
  "NEXTPOSITION": null,
  "RESULTSET": [
    {
      "SERIES_CODE": "STRDCLUCON",
      "VALUES": {
        "SURVEY_DATES": [19980105, 19980106],
        "VALUES": [0.49, null]
      }
    }
  ]
}
```

## Data Layer API (`getDataLayer`)

Observed top-level keys:

- `STATUS`, `MESSAGEID`, `MESSAGE`, `DATE`, `PARAMETER`, `NEXTPOSITION`, `RESULTSET`

Observed success example (trimmed):

```json
{
  "STATUS": 200,
  "MESSAGEID": "M181000I",
  "MESSAGE": "Successfully completed",
  "DATE": "2026-02-21T23:41:58.086+09:00",
  "PARAMETER": {
    "DB": "MD10",
    "LAYER1": "*",
    "FREQUENCY": "Q",
    "STARTPOSITION": "1"
  },
  "NEXTPOSITION": 255,
  "RESULTSET": [
    {
      "SERIES_CODE": "DLDDLKY45090_DLDD3DBTTL",
      "VALUES": {
        "SURVEY_DATES": [201001, 201004],
        "VALUES": [1387782, 1412814]
      }
    }
  ]
}
```

## Error Shape

Observed error responses (HTTP 400) were compact:

```json
{
  "STATUS": 400,
  "MESSAGEID": "M181018E",
  "MESSAGE": "Invalid frequency",
  "DATE": "2026-02-21T..."
}
```

Examples observed on February 21, 2026:

- invalid DB (`getMetadata`): `M181005E`, `Invalid database name`
- invalid code format (`getDataCode`): `M181001E`, `Invalid input parameters`
- invalid frequency (`getDataLayer`): `M181018E`, `Invalid frequency`
