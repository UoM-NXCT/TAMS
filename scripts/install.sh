#!/bin/bash

echo "Installing packages..."
python -m pip install --upgrade pip
pip install poetry
poetry install