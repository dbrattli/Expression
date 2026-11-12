# Maintaining documentation

Documentation is part of the public API. Update the relevant guide and reference when a
public feature changes.

## Before opening a pull request

- Add or update a task-focused example for changed user-visible behavior.
- Keep code examples compatible with supported Python versions and public APIs.
- Explain unfamiliar terms in plain language before using their technical name.
- Link a guide to the detailed API reference and vice versa.
- Update `README.py`, then run `uv run ./make_readme.sh`, when the project overview or
  quick-start experience changes.
- Build the book locally with `uv run --with-requirements docs/requirements.txt jb build docs`.

Examples should be deterministic, avoid network and user input, and show a meaningful
assertion or output where practical. Prefer a small complete workflow over isolated API
calls.
