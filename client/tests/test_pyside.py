"""Tests for the Qt styles (via PySide6)."""
import unittest

from PySide6.QtWidgets import QStyleFactory


class TestPyside6(unittest.TestCase):
    """Test the PySide6 module."""

    def test_style_keys(self) -> None:
        """Test PySide6 can load the styles.

        The current problem is that, on Linux and via Pip, PySide6 defaults to Fusion
        and cannot find the system styles.
        """
        # Get the list of styles
        keys: list[str] = QStyleFactory.keys()

        # Fusion is the fallback style absent a system style
        assert "Fusion" in keys
