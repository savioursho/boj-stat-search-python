# Development Guide

This guide is for contributors maintaining `boj_stat_search` internals, tests,
and release/compliance workflows.

It complements the user-focused documentation in `docs/user_guide/` and the
raw BOJ endpoint reference in `docs/api_manual/`.

## Guide Map

1. [Architecture](./architecture.md): Functional Core / Imperative Shell
   boundaries and module placement rules.
2. [Testing Strategy](./testing.md): Architecture-aligned test strategy: heavy
   core tests, thin shell tests.
3. [Release Process and Branch Policy](./release_process.md): Branch model,
   release flow, version bumping, tagging, and pre-release checks.
4. [Metadata Licensing Determination](./metadata_licensing.md): BOJ metadata
   redistribution determination and operational compliance rules.

## How To Use This Guide

- Start with [Architecture](./architecture.md) before adding or moving modules.
- Follow [Testing Strategy](./testing.md) when adding or changing behavior.
- Use [Release Process and Branch Policy](./release_process.md) for release
  preparation and tagging.
- Re-check [Metadata Licensing Determination](./metadata_licensing.md) whenever
  metadata generation/distribution behavior changes.
