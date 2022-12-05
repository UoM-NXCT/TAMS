#!/bin/bash

echo "Formatting with ssort..."
python -m poetry run ssort .

echo "Formatting with isort..."
python -m poetry run isort . --profile black

echo "Formatting with black..."
python -m poetry run black .

$SHELL