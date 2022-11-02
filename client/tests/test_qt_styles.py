""" Test Qt styles

Tests for the Qt styles (via PySide6).
"""
import PySide6.QtWidgets


class TestStyles:
    """Test Qt styles.

    The current problem is that, on Linux and via Pip, PySide6 defaults to Fusion and
    cannot find the system styles.
    """

    def test_style_keys(self):
        """Test that PySide6 can load the styles."""
        keys = PySide6.QtWidgets.QStyleFactory.keys()
        print(f"{keys=}")
        assert "Fusion" in keys


if __name__ == "__main__":
    TestStyles().test_style_keys()
