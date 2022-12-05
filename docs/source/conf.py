"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import sphinx_rtd_theme  # pylint: disable=import-error

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project: str = "TAMS"
copyright: str = "2022, NXCT et al"
author: str = "NXCT et al"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = ["sphinx_rtd_theme"]

templates_path: list[str] = ["_templates"]
exclude_patterns: list[str | None] = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme: str = "sphinx_rtd_theme"
html_static_path: list[str] = ["_static"]
