# Documentation

## Sections

- **[API Manual](./api_manual/)** — Documents the raw Bank of Japan Stat-Search Web API: endpoints, parameters, response shapes, and discrepancies between the official manual and observed behavior.
- **[User Guide](./user_guide/)** — Explains how to use the `boj_stat_search` Python package: two-layer API architecture, getting started, querying data, pagination, error handling, and layer tree display. Includes wrapper conveniences such as `Code` (`DB'CODE` input) and cache-based DB resolution for `get_data_code`.
- **[Development Guide](./development_guide/README.md)** — Contributor docs for internal architecture boundaries, testing strategy, release process, and metadata licensing/compliance.

## Data Code Usability

`boj_stat_search` provides higher-level Data Code ergonomics beyond the raw BOJ API:

- Accept BOJ UI-style `DB'CODE` input via `Code` (for example, `Code("IR01'MADR1Z@D")`).
- Allow omitting `db` in `get_data_code` when it can be inferred from local cached catalog data.
- Expose `resolve_db` for explicit cache-only DB lookup by series code.

For usage details and examples, see [User Guide: Querying Data](./user_guide/querying_data.md).
