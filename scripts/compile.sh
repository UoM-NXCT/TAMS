#!/bin/bash

echo "Compiling with pyinstaller..."
python -m poetry run pyinstaller \
--add-data="client/settings/*;client/settings/" \
--add-data="client/resources/*;client/resources/" \
--windowed client/__main__.py --name "TAMS"

$SHELL

python -m poetry run pyinstaller --windowed client/__main__.py --name "TAMS"