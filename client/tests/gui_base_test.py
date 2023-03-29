import sys
from unittest import TestCase

from PySide6.QtWidgets import QApplication, QMainWindow


class GuiBaseTest(TestCase):
    @classmethod
    def setUp(cls) -> None:
        cls.app: QApplication = QApplication(sys.argv)
        cls.gui: QMainWindow = QMainWindow()

    @classmethod
    def tearDown(cls) -> None:
        cls.gui.close()

    def gui_loaded(self) -> None:
        """Test the GUI is shown."""
        assert self.gui.show

    def test_common(self):
        self.gui_loaded()
