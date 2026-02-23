# Functional Core / Imperative Shell Architecture

Part of the [Development Guide](./README.md).

This project follows the Functional Core / Imperative Shell pattern at the
directory level.

## Directory Structure

```text
src/boj_stat_search/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── database.py
│   ├── formatter.py
│   ├── parser.py
│   ├── types.py
│   ├── url_builder.py
│   └── validator.py
└── shell/
    ├── __init__.py
    ├── api.py
    ├── client.py
    ├── catalog/
    │   ├── __init__.py
    │   ├── exporter.py
    │   ├── loader.py
    │   └── search.py
    ├── display.py
    └── cli.py
```

## Boundary Rules

`core/`:
- Pure logic only.
- No side effects.
- No HTTP, file I/O, console output, or mutable runtime state.
- Includes value objects, parsers, validators, formatting, URL builders, and
  pure data models.

`shell/`:
- Side effects only.
- Handles HTTP requests, file reads/writes, console output, and stateful
  clients.
- Should delegate decisions and transformations to `core/`.

Dependency direction:
- `shell/` may import `core/`.
- `core/` must never import `shell/`.

## Placement Guide

Use this checklist when adding code:

| Change type | Location |
|---|---|
| New validation/type/normalization logic | `core/` |
| New parsing or response-shape mapping logic | `core/` |
| New pure formatting utility | `core/` |
| New HTTP endpoint integration | `shell/api.py` |
| New file cache/export behavior | `shell/catalog/` |
| New client/session behavior | `shell/client.py` |
| New CLI command | `shell/cli.py` |
| New terminal display behavior (`print`) | `shell/display.py` |

## Practical Decision Criterion

If importing and calling the module causes no observable effect on the outside
world, it belongs in `core/`. Otherwise it belongs in `shell/`.
