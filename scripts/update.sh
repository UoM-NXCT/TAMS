#!/bin/bash

echo "Updating packages..."
python -m pip install --upgrade pip
python -m poetry update
