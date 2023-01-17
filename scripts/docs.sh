#!/bin/bash

echo "Building documentation..."
cd docs || exit
python -m poetry run sphinx-build -b html source build
cd ..
