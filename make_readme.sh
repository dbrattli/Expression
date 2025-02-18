#!/bin/bash

jupytext --to markdown --pipe-fmt markdown --pipe "sed '/<!-- #raw -->/,/<!-- #endraw -->/d'" README.py -o README.md