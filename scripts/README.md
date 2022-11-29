These scripts may be useful for those developing this project. They are not intended for
general use.

- [compile.sh](compile.sh): compiles the project as a binary executable using [PyInstaller](https://pyinstaller.org/en/stable/)
- [format.sh](format.sh): formats the code to be consisted and easy to read using:
  - [ssort](https://github.com/bwhmather/ssort)
  - [isort](https://pycqa.github.io/isort/)
  - [black](https://black.readthedocs.io/en/stable/)
- [lint.sh](lint.sh): checks the code for errors using:
  - [ssort](https://github.com/bwhmather/ssort)
  - [isort](https://pycqa.github.io/isort/) (with `--profile black`)
  - [black](https://black.readthedocs.io/en/stable/)
  - [mypy](https://github.com/python/mypy) (with `--strict`)
  - [pylint](https://pylint.pycqa.org/en/latest/)
- [install.sh](install.sh)/[update.sh](update.sh): install/update packages using:
  - [pip](https://pip.pypa.io/en/stable/)
  - [poetry](https://python-poetry.org/)

# Instructions

All scripts are intended to be run from the root of the project.

## Linux/macOS/etc.

Give execute permission to the script, if it needs it:

```bash
chmod +x scripts/install.sh
```

Run the script:

```bash
./scripts/install.sh
```

## Windows

Consider using [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) or [Git Bash](https://gitforwindows.org/).

Then, follow the instructions for Linux/macOS/etc.
