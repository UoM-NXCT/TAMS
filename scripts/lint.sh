#!/bin/bash

echo "Checking with ssort..."
poetry run ssort --check .

echo "Checking with isort..."
poetry run isort --check-only --profile black .

echo "Checking with black..."
poetry run black --check .

echo "Checking with mypy..."
poetry run mypy client/db --strict
poetry run mypy client/runners --strict
poetry run mypy client/settings --strict
poetry run mypy client/utils --strict

echo "Checking with pylint..."
poetry run pylint client

$SHELL