default: check

# Install the project and all optional dependencies.
install:
    poetry install --all-extras

# Run the complete test suite.
test:
    poetry run pytest

# Run all formatting, linting, type-checking, and repository checks.
lint:
    poetry run pre-commit run --all-files --show-diff-on-failure

# Run the same validation expected before opening a pull request.
check: lint test

# Build the source and wheel distributions.
build:
    poetry build
