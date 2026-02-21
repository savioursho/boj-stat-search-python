# BOJ Web API Guide

This directory documents the **original Bank of Japan Stat-Search Web API**:

- `https://www.stat-search.boj.or.jp/api/v1/getMetadata`
- `https://www.stat-search.boj.or.jp/api/v1/getDataCode`
- `https://www.stat-search.boj.or.jp/api/v1/getDataLayer`

It does **not** document `boj-stat-search` helper functions.  
For wrapper usage, see `docs/user_guide/`.

Official manual (source):  
`https://www.stat-search.boj.or.jp/info/api_manual.pdf`

## Read In Order

1. [Request Basics](./request_basics.md)
2. [Response Shapes](./response_shapes.md)
3. [Manual vs Actual](./manual_vs_actual.md)

## Scope

- Raw endpoint URLs and query parameters
- Response JSON structure for success and error cases
- Differences between official manual and observed live responses

## Verification Date

Observed response notes in this folder are based on live API calls run on **February 21, 2026**.
