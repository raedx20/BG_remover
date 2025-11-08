"""
Output & Naming tab.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QGroupBox, QTextEdit
)
import os


class OutputTab(QWidget):
    """Output & Naming tab widget."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Output folder group
        folder_group = QGroupBox("Output Folder")
        folder_layout = QVBoxLayout()

        folder_row = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Select output folder for processed images...")
        self.folder_edit.setText(self.config['output'].get('output_folder', ''))

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)

        folder_row.addWidget(self.folder_edit)
        folder_row.addWidget(browse_btn)
        folder_layout.addLayout(folder_row)

        # Note: output folder must differ from input
        note_label = QLabel("Note: Output folder must be different from input folder.")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        folder_layout.addWidget(note_label)

        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Overwrite policy group
        policy_group = QGroupBox("Overwrite Policy")
        policy_layout = QVBoxLayout()

        policy_layout.addWidget(QLabel("If output file already exists:"))

        self.policy_combo = QComboBox()
        self.policy_combo.addItem("Skip (leave existing file)", "skip")
        self.policy_combo.addItem("Overwrite (replace existing file)", "overwrite")
        self.policy_combo.addItem("Disambiguate (add number suffix)", "disambiguate")

        # Set current value
        current_policy = self.config['output'].get('overwrite_policy', 'disambiguate')
        index = self.policy_combo.findData(current_policy)
        if index >= 0:
            self.policy_combo.setCurrentIndex(index)

        policy_layout.addWidget(self.policy_combo)
        policy_group.setLayout(policy_layout)
        layout.addWidget(policy_group)

        # Naming rules group (informational, fixed)
        naming_group = QGroupBox("Naming Rules (Fixed)")
        naming_layout = QVBoxLayout()

        naming_info = QTextEdit()
        naming_info.setReadOnly(True)
        naming_info.setMaximumHeight(120)
        naming_info.setHtml("""
<p>Output files are automatically named with orientation suffixes:</p>
<ul>
<li><b>_PRT</b>: Portrait (H &gt; W × 1.05)</li>
<li><b>_LSC</b>: Landscape (W &gt; H × 1.05)</li>
<li><b>_SQR_LSC</b>: Square/Near-square (±5%)</li>
</ul>
<p>All output files are saved as PNG with RGBA transparency.</p>
        """)

        naming_layout.addWidget(naming_info)
        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)

        layout.addStretch()
        self.setLayout(layout)

    def browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.folder_edit.text() or os.path.expanduser("~")
        )

        if folder:
            self.folder_edit.setText(folder)
            self.config['output']['output_folder'] = folder

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        return {
            'output': {
                'output_folder': self.folder_edit.text(),
                'overwrite_policy': self.policy_combo.currentData()
            }
        }

    def validate(self, input_folder):
        """
        Validate output settings.

        Args:
            input_folder: Input folder path for comparison

        Returns:
            Tuple of (is_valid, error_message)
        """
        output_folder = self.folder_edit.text()

        if not output_folder:
            return False, "Output folder is not specified."

        # Check that output != input
        if os.path.normpath(output_folder) == os.path.normpath(input_folder):
            return False, "Output folder must be different from input folder."

        return True, ""
