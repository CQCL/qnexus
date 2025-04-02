#!/bin/bash

# Script to run formatting, liniting and type checking tools

uv run isort qnexus/ 
uv run isort tests/
uv run isort integration/
uv run black .

uv run pylint qnexus/
uv run pylint tests/
uv run pylint integration/

uv run mypy qnexus/ --namespace-packages
uv run mypy tests/ --namespace-packages
uv run mypy integration/ --namespace-packages
