#!/bin/bash

echo "Formatting with ssort..."
python -m poetry run ssort .

echo "Formatting with isort..."
python -m poetry run isort .

echo "Formatting with black..."
python -m poetry run black .

echo "Formatting with sqlfluff..."
python -m poetry run sqlfluff fix . --dialect postgres