# Two-Layer API Architecture — Contributor Guide

This document explains how the two-layer API architecture affects where new code should be added.

## Layer Responsibilities

### Low-Level API

A faithful, thin wrapper around the original BOJ API.

- Input parameters mirror the raw API (plain strings, no value objects).
- Output structure mirrors the raw API response shape.
- No validation, no pagination handling, no multi-request resolution.
- Purpose: provide a stable, predictable 1-to-1 mapping to the upstream API.

### High-Level API

A user-facing layer that adds convenience and safety.

- Accepts value objects (`Frequency`, `Layer`, `Period`) for validation and normalization.
- Automatic pagination (fetches all pages transparently).
- Transparent multi-request resolution: query patterns that require multiple API calls under the hood are handled automatically so the caller makes a single function call.
- Purpose: let users focus on *what* data they want, not *how* to retrieve it.

## Dependency Direction

- High-level depends on low-level. **Never the reverse.**
- Both layers are part of the public API — users can choose whichever suits their needs.

## Where Does New Code Go?

Use this checklist when adding or modifying functionality:

| Change type | Target layer |
|---|---|
| New upstream API parameter passthrough | Low-level |
| New response field passthrough | Low-level |
| New convenience helper (auto-pagination, multi-request, etc.) | High-level |
| New value object or enum | High-level |
| New validation rule | High-level |
| New `BojClient` method | High-level |
| New CLI subcommand | High-level (CLI wraps high-level functions) |
| Bug fix in raw API mapping | Low-level |
| Bug fix in validation or convenience logic | High-level |

## API Styles per Layer

| Layer | Functional API | Client API (`BojClient`) | CLI |
|---|---|---|---|
| Low-level | Yes | — | — |
| High-level | Yes | Yes | Yes |

The client API adds HTTP connection reuse and automatic throttling, which are primarily useful in batch workflows where the high-level API is the natural choice.

The CLI tracks the high-level functional API. Each CLI subcommand is a thin wrapper that parses arguments, calls the corresponding high-level function, and formats the output. Low-level API features are not exposed through the CLI — users who need that level of control are expected to use the Python API directly.

## Key Principles

1. **Keep the low-level layer stable.** Changes should track upstream API changes only.
2. **Add convenience in the high-level layer.** If you're adding validation, pagination, or multi-request logic, it belongs in the high-level layer.
3. **Respect the dependency direction.** High-level imports low-level. Low-level must never import from high-level.
