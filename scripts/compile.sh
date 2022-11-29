#!/bin/bash

echo "Compiling..."
poetry run pyinstaller \
--add-data="client/settings/*;client/settings/" \
--add-data="client/resources/*;client/resources/" \
--windowed client/__main__.py --name "TAMS"

$SHELL