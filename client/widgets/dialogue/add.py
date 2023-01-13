"""
This window lets users add scans to the library.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from client.library import NikonScan, get_relative_path, local_path
from client.runners.add_scan import AddScan
from client.utils.file import create_dir


class AddToLibraryProgress(QDialog):
    """Progress window for adding scans to the library."""

    def __init__(self, runner: AddScan, parent_dlg: QDialog) -> None:
        """Initialize the window."""

        super().__init__(parent=parent_dlg)

        self.setWindowTitle("Adding data to library")
        layout: QVBoxLayout = QVBoxLayout()
        label: QLabel = QLabel("Adding data to library...")
        layout.addWidget(label)
        # TODO: Add progress bar
        # TODO: Add stop, pause, resume buttons
        # NOTE: Both tasks above should be very similar to what was done for the
        #  download functionality; it should be possible to copy and paste.
        self.setLayout(layout)

        self.threadpool: QThreadPool = QThreadPool()
        self.runner: AddScan = runner
        self.threadpool.start(self.runner)

        self.show()


class AddToLibrary(QDialog):
    """Window for adding scans to the library."""

    def _set_up_settings_window(self) -> None:
        """Create and arrange widgets in the project creation window."""

        header_label = QLabel("Add new scan to library")

        # Get scan format
        scan_fmt_label = QLabel("Select scan format:")
        self.scan_fmt = QComboBox()
        self.scan_fmt.addItems(("Nikon",))

        # Get scan location
        self.scan_loc_label = QLabel("Select scan location:")
        self.scan_loc_btn = QPushButton("Edit scan location")
        self.scan_loc_btn.clicked.connect(self.select_scan_loc)

        # Create the tree widget
        self.metadata_tree: QTreeWidget = QTreeWidget()
        self.metadata_tree.setColumnCount(1)
        # Hide the header; our tree is vertical so there is no reason to include it.
        self.metadata_tree.setHeaderHidden(True)

        # Make create project button
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_scan)

        # Create the layout for the settings window.
        v_box = QVBoxLayout()
        v_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_box.addWidget(header_label)
        v_box.addWidget(scan_fmt_label)
        v_box.addWidget(self.scan_fmt)
        v_box.addWidget(self.scan_loc_label)
        v_box.addWidget(self.scan_loc_btn)
        v_box.addWidget(self.metadata_tree)
        v_box.addWidget(add_btn)
        v_box.addStretch()
        self.setLayout(v_box)

    def __init__(self, scan_id: int, prj_id: int, *args, **kwargs) -> None:
        """Initialize the window."""

        super().__init__(*args, **kwargs)
        self.scan_id: int = scan_id
        self.prj_id: int = prj_id
        self.scan_loc: Path | None = None

        # Check the selected row
        if (
            self.parent().current_table() != "scan"
            or not self.parent().table_view.selectionModel().selectedRows()
        ):
            QMessageBox.warning(
                self,
                "No scan selected",
                (
                    "The 'add' action is for adding data to scans and does not, at"
                    " present, support adding projects. To add a project, you will have"
                    " to the scans associated to the project manually. Please select a"
                    " scan to add to the library."
                ),
            )
            self.close()
            return

        # Set up the settings window GUI.
        self.setMinimumSize(400, 300)
        self.setWindowTitle("Add to library")
        self._set_up_settings_window()
        self.show()

    def update_metadata_tree(self) -> None:
        """Update the metadata tree with the new scan metadata."""
        self.metadata_tree.clear()
        fmt: str = self.scan_fmt.currentText()
        match fmt:
            case "Nikon":
                scan = NikonScan(self.scan_loc)
                try:
                    metadata = scan.get_metadata()
                    items: list[QTreeWidgetItem] = []
                    for index, (key, value) in enumerate(metadata.items()):
                        item = QTreeWidgetItem([key])
                        child = QTreeWidgetItem([str(value)])
                        item.addChild(child)
                        items.append(item)
                    self.metadata_tree.insertTopLevelItems(0, items)
                    self.metadata_tree.expandAll()
                except FileNotFoundError:
                    QMessageBox.warning(
                        self,
                        "Metadata not found",
                        (
                            "Could not find scan metadata. Please check the correct"
                            " scan format has been selected and that the scan directory"
                            " is valid."
                        ),
                    )

            case _:
                raise NotImplementedError(f"Scan format {fmt} not implemented.")

    def select_scan_loc(self) -> None:
        """Select the scan location."""
        if self.scan_loc:
            init_dir: Path = self.scan_loc
        else:
            init_dir = Path.home()
        self.scan_loc = Path(
            QFileDialog.getExistingDirectory(
                self,
                caption="Select scan directory",
                dir=str(init_dir),
                options=QFileDialog.Option.ShowDirsOnly,
            )
        )
        if self.scan_loc:
            self.scan_loc_label.setText(f"Scan location: {self.scan_loc}")
        else:
            self.scan_loc_label.setText("Select scan location:")
            QMessageBox.warning(
                self,
                "No directory set",
                "No directory set. Please set a directory first.",
            )
        self.update_metadata_tree()

    def add_scan(self) -> None:
        """Add the scan to the library."""

        # For a scan to be saved, we need its project ID and scan ID as a minimum.

        # Create directories in local library if they don't exist
        relative_path: Path = get_relative_path(self.prj_id, self.scan_id)
        local_dir: Path = local_path(relative_path)
        create_dir(local_dir)

        fmt: str = self.scan_fmt.currentText()
        match fmt:
            case "Nikon":
                scan = NikonScan(self.scan_loc)
                runner = AddScan(self.prj_id, self.scan_id, scan)
                AddToLibraryProgress(runner, self)
            case _:
                raise NotImplementedError(f"Scan format {fmt} not implemented.")
