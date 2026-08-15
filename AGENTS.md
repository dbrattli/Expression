# Repository Guidelines

## Project Structure & Module Organization

The `expression/` package contains the library. Core functional types and helpers live
in `expression/core/`; immutable collections are in `expression/collections/`;
computational-expression builders are in `expression/effect/`; and supporting APIs are
split between `expression/extra/` and `expression/system/`. Tests mirror these features
as `tests/test_<feature>.py`. User documentation lives under `docs/`. Treat `README.py`
as the source for the generated `README.md`; never edit `README.md` alone.

## Build, Test, and Development Commands

- `just install` creates the uv environment with optional Pydantic support.
- `just test` runs the complete test suite configured in `pyproject.toml`.
- `uv run pytest tests/test_option.py -k map` runs a focused test selection.
- `just lint` runs pre-commit across all files, reproducing CI lint, formatting,
  type-checking, and README checks; `just check` runs lint and tests together.
- `just build` creates source and wheel distributions.
- `uv run ./make_readme.sh` regenerates `README.md` after changing `README.py`.

Release automation runs through EasyBuild.ShipIt. Install the local tool manifest with
`dotnet tool restore` and use Conventional Commit subjects (`feat:`, `fix:`, `docs:`,
`chore:`, `ci:`, etc.); ShipIt uses these commits to generate `CHANGELOG.md` and open
release pull requests. Do not hand-edit generated release entries.

## Coding Style & Naming Conventions

Write Python compatible with 3.10 and follow PEP 8. Ruff enforces a 120-character line
limit, import ordering, Google-style docstrings, and the configured lint rules; Pyright
runs in strict mode. Use four-space indentation, `snake_case` for functions and modules,
`PascalCase` for classes and tagged-union types, and leading underscores for internal
symbols. Add precise type hints to public functions and methods. Preserve the project's
Pythonic, pipe-friendly APIs and avoid unnecessary operator overloading or exposed
recursion.

## Testing Guidelines

Use pytest functions named `test_<behavior>` in the matching `tests/test_*.py` module.
Keep tests deterministic and cover both fluent and functional APIs where relevant. Use
`pytest.mark.asyncio` for async behavior and Hypothesis for property-based invariants.
There is no stated numeric coverage threshold, but changes should exercise new branches,
error cases, and supported Python behavior. Run the full suite before submitting.

## Commit & Pull Request Guidelines

Recent commits favor short, imperative Conventional Commit subjects such as `fix:`,
`feat:`, `refactor:`, and `chore:`. Keep each commit focused. Pull requests should target
`main`, explain the user-visible behavior and design choices, link relevant issues, and
list verification commands. Add or update tests for code changes and include concise API
examples for public features. Update `README.py` or `docs/` when behavior documented to
users changes; include screenshots only for visual documentation changes.
