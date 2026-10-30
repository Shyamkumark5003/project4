# Day 4: apiclient

A small client for the Training Mock API (variant 1, books).

## Features
- Timeout on every call
- Retries with exponential backoff and jitter on 5xx and 429, respects Retry-After
- Pagination iterator `iter_books()`
- Pydantic validation of every record
- Tests use a fake transport and never touch the network

## Run
    uv sync
    uv run pytest -q

## Try against the mock server (start it first in starter_kit/mock_api)
    PYTHONPATH=. uv run python explore/live_check.py
