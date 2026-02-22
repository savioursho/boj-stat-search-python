# Metadata Licensing Determination

## Scope

This note documents whether this repository can redistribute BOJ Stat-Search
metadata files (for example `metadata/FM01.parquet`) that are generated from the
official Metadata API.

## Source Documents Reviewed

- `https://www.stat-search.boj.or.jp/info/api_notice.pdf`
- `https://www.stat-search.boj.or.jp/info/notice.html`

Reviewed on: **February 22, 2026**

## Determination

**Conditionally permitted.**

Redistribution of metadata is allowed when the following conditions are met:

1. Attribution/source display is included.
2. Required API credit statement is displayed when publishing a service that
   uses the API.
3. No unauthorized modification of source content is performed.
4. Commercial-purpose reproduction requires prior consultation with BOJ.
5. API usage must avoid high-frequency access patterns.

## Operational Rules For This Repository

1. Keep attribution in project docs and in `metadata/NOTICE.md`.
2. Treat generated metadata files as factual copies in a different file format
   (Parquet), without semantic edits to names/codes/categories/date fields.
3. If metadata redistribution is tied to commercial use, consult BOJ first
   (per site notice).
4. If operating a publicly available service that uses the API, notify
   `post.rsd17@boj.or.jp` with the requested subject format described in
   `api_notice.pdf`.
5. Treat BOJ source-site terms as governing terms for redistributed metadata
   files.

## Notes

- This is a project compliance record, not legal advice.
- BOJ may update terms without prior notice; re-check source URLs before each
  release that changes metadata distribution behavior.
