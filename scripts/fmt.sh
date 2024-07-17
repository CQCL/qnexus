#!/bin/bash

# Script to run formatting, liniting and type checking tools

poetry run isort .
poetry run black .

poetry run pylint qnexus/
poetry run pylint tests/
poetry run pylint integration/

poetry run mypy qnexus/ --namespace-packages
poetry run mypy tests/ --namespace-packages
poetry run mypy integration/ --namespace-packages