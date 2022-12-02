#!/bin/bash

echo "Formatting with ssort..."
poetry run ssort .

echo "Formatting with isort..."
poetry run isort . --profile black

echo "Formatting with black..."
poetry run black .

$SHELL