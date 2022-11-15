import sys
from unittest import TestCase

from PySide6.QtWidgets import QApplication

from client.gui import MainWindow


class GuiBaseTest(TestCase):

    @classmethod
    def setUp(cls) -> None:
        cls.app: QApplication = QApplication(sys.argv)
        cls.gui: MainWindow = MainWindow()

    @classmethod
    def tearDown(cls) -> None:
        cls.gui.close()

    def gui_loaded(self) -> None:
        """Test the GUI is shown."""

        self.assertTrue(self.gui.show)

    def window_title_seen(self) -> None:
        """Test the window title is correct."""

        self.assertEqual(self.gui.windowTitle(), "Tomography Archival Management Software")

    def test_common(self):
        self.gui_loaded()
        self.window_title_seen()