# TAMS

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

TAMS is an open-source tomography archival and management application released by the National X-ray Computed Tomography (NXCT), the UK's national lab-based X-ray computed tomography research facility.

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

TAMS is currently in development, so it does not yet have installation instructions and is not recommended for production use.

If you wish to use TAMS regardless, clone this repository, install the dependencies from `pyproject.toml`, and run the application.

```commandline
poetry run python -m client
```

### Windows installation instructions (WIP)

The Qt library depends on Postgres' library, which must be available in the path to load. You can do this by adding your Postgres installation bin folder to your path.

For example, Postgres is installed on my computer under `C:\Program Files\PostgreSQL\14\` (I'm using version 14). We need to add the Postgres `bin` folder to the `PATH` as this contains `libpq.dll` (Postgres Access Library), which Qt needs.

```commandline
SET PATH=%PATH%;C:\Program Files\PostgreSQL\14\bin
```

## Develop

Installation instructions are a bit different for those looking to develop the software.

### GUI

[Poetry](https://python-poetry.org/) is a mature package management system for Python. It uses Pip to install
packages and handle dependencies.

There are two main ways to use [Poetry](https://python-poetry.org/docs/basic-usage/).

The first way is to use `poetry run`.

```commandline
poetry run python client/gui.py
```

The second way is to use Poetry to generate a `requirements.txt` file and install the
requirements directly using the file with `pip`.

```commandline
poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt
python client/gui.py
```

### PostgreSQL server

You can use container software such as Podman and Docker to run the server in a container. Podman is preferred as it
because of it does not require a daemon or root privileges. However, you may prefer Docker if you run Windows or would
like greater community support (Docker is more commonly used).

##### Build and run

First build the container image by running:

```commandline
podman build -f db.Containerfile
```

Or,

```commandline
docker build . -f db.Containerfile
```

Then run the image:

```commandline
podman run -d --restart always --user postgres -p 5432:5432 --volume pgdata:/var/lib/postgres/data [IMAGE]
```

Or,

```commandline
docker run -d --restart always --user postgres -p 5432:5432 --volume pgdata:/var/lib/postgres/data [IMAGE]
```

##### Compose

You can also run the PostgreSQL server using the `compose.yml` file:

```commandline
podman-compose up db
```

Or,

```commandline
docker-compose up db
```

### Tests

#### pytest

Test the application using [pytest](https://docs.pytest.org/en/stable/).

```commandline
poetry run pytest client
```

You can also use `pytest` directly if you have it installed.

#### Type hints

This project uses type hints to help with development.

Use [mypy](http://mypy-lang.org/) to check type hints.

```commandline
poetry run mypy client
```

You can also use `mypy` directly if you have it installed.

However, `mypy` does not work with PySide6, so you should ignore some of its complaints.

## Issues

If you have found a bug, you can file it under the 'issues' tab. You can also request new features.

## Licence

This project is licenced under the [MIT licence](LICENCE).

## Warranty

TAMS is distributed in the hope that it will be useful, but with **absolutely no warranty**.

Read the [licence](LICENCE) for more information.
