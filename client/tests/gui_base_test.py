"""Base class for GUI tests."""
from __future__ import annotations

import sys
from unittest import TestCase

from PySide6.QtWidgets import QApplication, QMainWindow


class GuiBaseTest(TestCase):
    """Base class for GUI tests."""

    @classmethod
    def setUp(cls: TestCase) -> None:
        """Set up the GUI for testing."""
        cls.app = QApplication(sys.argv)
        cls.gui = QMainWindow()

    @classmethod
    def tearDown(cls: TestCase) -> None:
        """Tear down the GUI after testing."""
        cls.gui.close()

    def gui_loaded(self: TestCase) -> None:
        """Test the GUI is shown."""
        assert self.gui.show

    def test_common(self: TestCase) -> None:
        """Run common GUI tests."""
        self.gui_loaded()
