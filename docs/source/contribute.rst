Contributing
============

Thanks for your interest in contributing to the project!

Code
----

The code is hosted on `GitHub <https://github.com/UoM-NXCT/TAMS>`_.

If you'd like to contribute or request code, it helps to open an issue and ask questions about what you're thinking of working on.

You should also review all of the `open issues <https://github.com/UoM-NXCT/TAMS/issues>`_ on GitHub to see if there are any you'd like to tackle.

When you're ready to contribute code, open a pull request in the GitHub repository and one of the project maintainers will review it and possibly ask questions, request changes, reject it, or merge it into the project.

Starting Development
--------------------

TAMS is developed in Python.

To get started, clone the `Git repository <https://github.com/Uom-NXCT/TAMS/>`_.

Dependency Management
^^^^^^^^^^^^^^^^^^^^^

`Poetry <https://python-poetry.org/>`_ is used to manage dependencies.

To install Poetry, follow the `installation instructions <https://python-poetry.org/docs/#installation>`_.

There are two main ways to use Poetry to install dependencies and, for example, run the client. The first way is use Poetry directly.

.. code-block:: bash

    poetry install
    poetry run python -m client

The second way is to use Poetry to generate a ``requirements.txt`` file and install the requirements directly using the file with ``pip``.

.. code-block:: bash

    poetry export -f requirements.txt --output requirements.txt
    pip install -r requirements.txt
    python -m client

PostgreSQL server
^^^^^^^^^^^^^^^^^

TAMS uses a PostgreSQL database to store data. If you are developing this software, it is a good idea to run a local database server for testing.

You can use container software such as Podman and Docker to run the server in a container. Podman is preferred as it because of it does not require a daemon or root privileges. However, you may prefer Docker if you run Windows or would like greater community support (Docker is more commonly used).

Build and run
"""""""""""""

First build the container image by running:

.. code-block:: bash

    podman build . -t tams-postgres -f db.Containerfile

Or, with Docker:

.. code-block:: bash

    docker build . -t tams-postgres -f db.Containerfile

Then run the image:

.. code-block:: bash

    podman run -d --restart always --user postgres -p 5432:5432 --volume pgdata:/var/lib/postgres/data tams-postgres

Or, with Docker:

.. code-block:: bash

    docker run -d --restart always --user postgres -p 5432:5432 --volume pgdata:/var/lib/postgres/data tams-postgres

The database server will be available on port 5432 on the host machine.

Compose
"""""""

You can also run the database server using the ``compose.yml`` file in the root of the repository.

.. code-block:: bash

    podman-compose up db

Or, with Docker:

.. code-block:: bash

    docker-compose up db

Tests
^^^^^

This project uses `pytest <https://docs.pytest.org/en/stable/>`_ for testing.

To run the tests, run:

.. code-block:: bash

    poetry run pytest

Type checking
^^^^^^^^^^^^^

Python is a dynamically typed language. This means that the Python interpreter does type checking only as code runs, and that the type of a variable can change over its lifetime. This is a powerful feature, but it can also lead to bugs, unexpected behaviour, and security vulnerabilities. It can also make code difficult to read if the project becomes complex.

To help with this, TAMS uses Python's built-in type annotations `mypy <http://mypy-lang.org/>`_ to perform static type checking. This means that the type of a variable is checked before the code is run. This can help to catch bugs before they occur.

To run the type checker, run:

.. code-block:: bash

    poetry run mypy . --strict

Compile
^^^^^^^

Python is an interpreted language. This means that the Python interpreter reads the source code and executes it. This is a powerful feature, but it can also lead to performance issues. It can also make it difficult to distribute the code.

To help with this, TAMS uses `PyInstaller <https://www.pyinstaller.org/>`_ to compile the code into a single executable file. This means that the code is compiled into machine code before it is run.

Code style
----------

Please follow the code style of this project when contributing code. Doing so will make it easier for other developers to read and understand your code.

If something is not covered by the code style, please use your best judgement and try to adhere to modern Python best practices.

Black
^^^^^

This project uses `Black <https://black.readthedocs.io/en/stable/>`_ to format code. Black is an opinionated code formatter that will automatically format your code to follow the project's code style.

To format your code with Black, run:

.. code-block:: bash

    poetry run black .

isort
^^^^^

This project uses `isort <https://pycqa.github.io/isort/>`_ to sort imports. It will sort imports alphabetically, and automatically separated into sections and by type

To sort your imports with isort, run:

.. code-block:: bash

    poetry run isort . --profile black

mypy
^^^^

This project uses `mypy <http://mypy-lang.org/>`_ to perform static type checking.

This project uses mypy's `strict mode <http://mypy-lang.org/docs/strict.html>`_. This means that mypy will check your code for a number of common errors, including:

-   Missing type annotations
-   Incorrect type annotations
-   Incorrect use of generics

This means you should use type annotations in any code you contribute.

For example, the following function takes an integer and string, and returns a string:

.. code-block:: python

    def greet(age, name):
        """Greet someone by name and age."""
        next_age = age + 1
        msg = f"Hello, {name}! You will be {next_age} next year."
        return msg

However, the function will not work as expected if the arguments are not the correct type. For example, someone could call the function like this:

.. code-block:: python

    greet("ten", "Alice")

This is a problem as the function expects the age as an integer. By using type annotations, we can catch this error before the code is run:

.. code-block:: python

    def greet(age: int, name: str) -> str:
        """Greet someone by name and age."""
        next_age: int = age + 1
        msg: str = f"Hello, {name}! You will be {next_age} next year."
        return msg

To run mypy, run:

.. code-block:: bash

    poetry run mypy . --strict

When running mypy on the code above, it will report the following error:

.. code-block:: bash

    error: Argument 1 to "greet" has incompatible type "str"; expected "int"

pylint
^^^^^^

This project uses `pylint <https://pylint.pycqa.org/en/latest/>`_ to check code for common errors and style issues.

To run pylint, run:

.. code-block:: bash

    poetry run pylint .

Variable names
^^^^^^^^^^^^^^

Variable names should be descriptive and follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/#naming-conventions>`_.

In practice, this means that variable names should be lowercase and use underscores to separate words. For example:

.. code-block:: python

    player_score = 1

Rather than:

.. code-block:: python

    playerScore = 1

However, this project uses PySide6 which interfaces with the C++ Qt library. This means that some variable names will be camelCase and not follow PEP 8. In this project, use snake_case to clarify where PySide6 ends and the project code begins.
