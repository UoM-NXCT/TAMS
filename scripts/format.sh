#!/bin/bash

echo "Formatting with ssort..."
python -m poetry run ssort .

echo "Formatting with ruff..."
python -m poetry run ruff check . --fix

echo "Formatting with black..."
python -m poetry run black .

echo "Formatting with sqlfluff..."
python -m poetry run sqlfluff fix . --dialect postgres