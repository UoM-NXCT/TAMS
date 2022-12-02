#!/bin/bash

echo "Building documentation..."
cd docs || exit
poetry run sphinx-build -b html source build
cd ..