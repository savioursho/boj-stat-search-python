# Manual vs Actual

Differences between the official API manual and live responses observed on **February 21, 2026**.

## Summary Table

| Topic | Manual Description (paraphrased) | Observed Actual Response |
| --- | --- | --- |
| Language-dependent output tags | Output tags differ by language setting | `lang=en` mostly returns EN fields only; `lang=jp` responses include JP fields and also EN companion fields in observed payloads |
| Success message text | Described by message IDs (for example normal completion) | `lang=en` returns `"Successfully completed"`; default/JP returns Japanese message text |
| Error semantics | `STATUS` indicates success (`200`) or error (`400` etc.) | HTTP status also matched body status in observed calls (`200` for success, `400` for invalid input) |
| `PARAMETER` echo values | Parameters are output; unspecified values are blank | Observed exactly this behavior: omitted `format`/`lang` show empty strings, explicitly set values show uppercase (`JSON`, `EN`) |
| `NEXTPOSITION` when no continuation | JSON may show `null` | Observed `null` in data code response without continuation; integer when continuation exists |

## Concrete Observations

1. Metadata (`getMetadata`) with `lang=jp` returned both JP and EN label/unit/category/note fields in one payload.
2. Data APIs (`getDataCode`, `getDataLayer`) returned:
   - `PARAMETER`
   - `NEXTPOSITION`
   - `RESULTSET[*].VALUES.SURVEY_DATES`
   - `RESULTSET[*].VALUES.VALUES`
3. Error payloads were short and did not include `PARAMETER`/`RESULTSET`.

## Reproducible Verification Snippet

```python
import httpx

urls = [
    "https://www.stat-search.boj.or.jp/api/v1/getMetadata?db=FM01&format=json&lang=en",
    "https://www.stat-search.boj.or.jp/api/v1/getDataCode?db=FM01&code=STRDCLUCON&format=json&lang=en",
    "https://www.stat-search.boj.or.jp/api/v1/getDataLayer?db=MD10&frequency=Q&layer=*&format=json&lang=en&startPosition=1",
]

for url in urls:
    r = httpx.get(url, timeout=30)
    data = r.json()
    print(url)
    print(r.status_code, list(data.keys()))
```

## Guidance for Consumers

- Validate both HTTP status and body `STATUS`.
- Parse fields defensively:
  - do not assume JP-only or EN-only label keys in all contexts,
  - allow missing optional sections on error responses.
- Treat this page as time-sensitive and re-verify periodically.
