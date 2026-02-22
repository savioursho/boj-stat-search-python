# Release Process and Branch Policy

## Branch Structure

| Branch | Purpose |
|---|---|
| `main` | Stable, released code. Each merge corresponds to a tagged release. |
| `develop` | Integration branch. Features and fixes are merged here first. |
| `release/vX.Y.Z` | Short-lived branch for preparing a specific release (version bump, final fixes). |
| `feat/<name>` | Feature branches. Created from `develop`, merged back into `develop` via PR. |

## Branch Flow

```
feat/xxx ──► develop ──► main
                ▲           ▲
                │           │
          release/vX.Y.Z ──┘ (tag: vX.Y.Z)
```

1. Feature branches are created from `develop` and merged back into `develop`.
2. When `develop` is ready for release, a `release/vX.Y.Z` branch is created from `develop`.
3. The release branch is merged into `develop`, then `develop` is merged into `main`.
4. A version tag and GitHub release are created on `main`.

## Release Steps

### 1. Create a release branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/vX.Y.Z
```

### 2. Bump the version

Update the `version` field in `pyproject.toml`:

```toml
[project]
version = "X.Y.Z"
```

### 3. Run pre-merge checks

```bash
uv run ruff format
uv run ruff check src tests
uv run pytest -q
```

All checks must pass before proceeding.

### 4. Merge the release branch into develop

- Push the release branch and open a PR targeting `develop`.
- Merge the PR after review.

### 5. Merge develop into main

- Open a PR from `develop` to `main`.
- Merge the PR after review.

### 6. Tag and release

```bash
git fetch origin main
git tag vX.Y.Z origin/main
git push origin vX.Y.Z
```

Then create a GitHub release:

```bash
gh release create vX.Y.Z --title "vX.Y.Z" --generate-notes
```

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — incompatible API changes.
- **MINOR** — new functionality in a backwards-compatible manner.
- **PATCH** — backwards-compatible bug fixes.
