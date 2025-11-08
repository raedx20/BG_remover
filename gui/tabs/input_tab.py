"""
Input tab for source folder and file selection.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTextEdit, QFileDialog, QGroupBox
)
from PyQt5.QtCore import pyqtSignal
import os


class InputTab(QWidget):
    """Input tab widget."""

    files_scanned = pyqtSignal(list)  # Signal emitted when files are scanned

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.scanned_files = []
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Source folder group
        folder_group = QGroupBox("Source Folder")
        folder_layout = QVBoxLayout()

        folder_row = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Select source folder containing images...")
        self.folder_edit.setText(self.config['input'].get('source_folder', ''))

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)

        folder_row.addWidget(self.folder_edit)
        folder_row.addWidget(browse_btn)
        folder_layout.addLayout(folder_row)

        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Extensions group
        ext_group = QGroupBox("File Extensions")
        ext_layout = QVBoxLayout()

        self.ext_edit = QLineEdit()
        extensions = self.config['input'].get('extensions', ['jpg', 'jpeg', 'png', 'webp'])
        self.ext_edit.setText(', '.join(extensions))
        self.ext_edit.setPlaceholderText("e.g., jpg, jpeg, png, webp")

        ext_layout.addWidget(QLabel("Extensions (comma-separated):"))
        ext_layout.addWidget(self.ext_edit)

        ext_group.setLayout(ext_layout)
        layout.addWidget(ext_group)

        # Recursive checkbox
        self.recursive_check = QCheckBox("Scan subfolders recursively")
        self.recursive_check.setChecked(self.config['input'].get('recursive', True))
        layout.addWidget(self.recursive_check)

        # Scan button
        scan_btn = QPushButton("Scan for Images")
        scan_btn.clicked.connect(self.scan_images)
        scan_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        layout.addWidget(scan_btn)

        # Results display
        results_group = QGroupBox("Detected Images")
        results_layout = QVBoxLayout()

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        self.results_text.setPlaceholderText("Click 'Scan for Images' to detect files...")

        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        layout.addStretch()
        self.setLayout(layout)

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Source Folder",
            self.folder_edit.text() or os.path.expanduser("~")
        )

        if folder:
            self.folder_edit.setText(folder)
            self.config['input']['source_folder'] = folder

    def scan_images(self):
        """Scan for images in selected folder."""
        from core.utils import scan_images

        folder = self.folder_edit.text()

        if not folder or not os.path.isdir(folder):
            self.results_text.setPlainText("Error: Please select a valid folder.")
            return

        # Get extensions
        ext_text = self.ext_edit.text()
        extensions = [ext.strip() for ext in ext_text.split(',') if ext.strip()]

        if not extensions:
            self.results_text.setPlainText("Error: Please specify at least one extension.")
            return

        # Update config
        self.config['input']['extensions'] = extensions
        self.config['input']['recursive'] = self.recursive_check.isChecked()

        # Scan
        try:
            files = scan_images(folder, extensions, self.recursive_check.isChecked())
            self.scanned_files = files

            # Display results
            if files:
                result_text = f"Found {len(files)} image(s):\n\n"
                for f in files[:50]:  # Show first 50
                    result_text += f"  • {os.path.relpath(f, folder)}\n"

                if len(files) > 50:
                    result_text += f"\n  ... and {len(files) - 50} more"

                self.results_text.setPlainText(result_text)

                # Emit signal
                self.files_scanned.emit(files)
            else:
                self.results_text.setPlainText("No images found matching the criteria.")

        except Exception as e:
            self.results_text.setPlainText(f"Error scanning: {str(e)}")

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        extensions = [ext.strip() for ext in self.ext_edit.text().split(',') if ext.strip()]

        return {
            'input': {
                'source_folder': self.folder_edit.text(),
                'extensions': extensions,
                'recursive': self.recursive_check.isChecked()
            }
        }
