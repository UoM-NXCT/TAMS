"""
Toggle full screen mode action.
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from client.gui import MainWindow


def toggle_full_screen(main_window: MainWindow, is_checked: bool) -> None:
    """Toggle full screen mode."""

    if is_checked:
        main_window.showFullScreen()
    else:
        main_window.showNormal()
