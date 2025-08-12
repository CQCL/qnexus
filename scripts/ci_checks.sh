#!/usr/bin/env bash
uv run mypy qnexus/ tests/ integration/
uv run ruff format --check
uv run ruff check
