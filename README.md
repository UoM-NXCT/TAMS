# TAMS

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![ReadTheDocs](https://img.shields.io/readthedocs/tams-nxct)](https://tams-nxct.readthedocs.io/en/latest/)

TAMS is an open-source tomography archival and management application released by the 
National X-ray Computed Tomography (NXCT), the UK's national lab-based X-ray computed 
tomography research facility.

It aims to make storing and accessing data easy and quick.

## Table of Contents

- [Get started](#get-started)
- [Develop](#develop)
  - [GUI](#gui)
  - [PostgreSQL server](#postgresql-server)
  - [Tests](#tests)
- [Issues](#issues)
- [Licence](#licence)
- [Warranty](#warranty)

## Get started

TAMS is currently in development, so it does not yet have installation instructions and 
is not recommended for production use.

If you wish to use TAMS regardless, clone this repository, install the dependencies from
`pyproject.toml`, and run the application.

```commandline
poetry run python -m client
```

## Documentation

The documentation is hosted [online](https://tams-nxct.readthedocs.io/en/latest/). You 
can also build the documentation locally by executing the following command from the 
`docs/` directory:

```commandline
poetry run sphinx-build -b html source build
```

## Contribute

This project is open to contributions. Read the 
[contributing guidelines](https://tams-nxct.readthedocs.io/en/latest/contribute.html) 
for more information.

## Licence

The code is released under the [MIT licence](LICENCE). The documentation is licenced
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Warranty

TAMS is distributed in the hope that it will be useful, but with **absolutely no 
warranty**.

Read the [software licence](LICENCE) for more information.
