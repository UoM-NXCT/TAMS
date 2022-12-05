#!/bin/bash

echo "Installing packages..."
python -m pip install --upgrade pip
python -m pip install poetry
python -m poetry install

$SHELL