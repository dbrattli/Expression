default: check

# Install the project and all optional dependencies.
install:
    uv sync --all-extras

# Run the complete test suite.
test:
    uv run pytest

# Run all formatting, linting, type-checking, and repository checks.
lint:
    uv run pre-commit run --all-files --show-diff-on-failure

# Run the same validation expected before opening a pull request.
check: lint test

# Build the source and wheel distributions.
build:
    uv build
