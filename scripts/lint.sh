#!/bin/bash

echo "Checking with ssort..."
python -m poetry run ssort --check .

echo "Checking with isort..."
python -m poetry run isort --check-only --profile black .

echo "Checking with black..."
python -m poetry run black --check .

echo "Checking with mypy..."
python -m poetry run mypy client/db --strict
python -m poetry run mypy client/runners --strict
python -m poetry run mypy client/settings --strict
python -m poetry run mypy client/utils --strict

echo "Checking with pylint..."
python -m poetry run pylint client

echo "Checking with flake8..."
python -m poetry run flake8 client

echo "Checking with sqlfluff..."
python -m poetry run sqlfluff lint . --dialect postgres

$SHELL