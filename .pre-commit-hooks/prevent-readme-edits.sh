#!/bin/bash

# Check if README.md was modified
if git diff --cached --name-only | grep -q "README.md"; then
    # Check if README.py was also modified
    if ! git diff --cached --name-only | grep -q "README.py"; then
        echo "ERROR: Direct modifications to README.md are not allowed"
        echo "Please make all documentation updates in README.py instead"
        exit 1
    fi
fi

exit 0
