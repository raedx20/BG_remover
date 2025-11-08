"""
Processing Mode tab.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QRadioButton, QCheckBox,
    QGroupBox, QTextEdit, QButtonGroup
)


class ModeTab(QWidget):
    """Processing Mode tab widget."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Mode selection group
        mode_group = QGroupBox("Processing Mode")
        mode_layout = QVBoxLayout()

        self.mode_group = QButtonGroup()

        # Mode A (Default)
        self.mode_a_radio = QRadioButton("Mode A: AI-first + Classical refine (Default)")
        self.mode_a_radio.setToolTip(
            "AI segmentation first, then refined with classical methods (GrabCut). "
            "White preservation applied. Auto-fallback to Hybrid if QC fails."
        )
        self.mode_group.addButton(self.mode_a_radio, 0)
        mode_layout.addWidget(self.mode_a_radio)

        mode_a_desc = QTextEdit()
        mode_a_desc.setReadOnly(True)
        mode_a_desc.setMaximumHeight(80)
        mode_a_desc.setHtml("""
<p><b>Best for:</b> Most product images, white-on-white products.<br>
<b>Process:</b> AI → White preservation → GrabCut refine → Edge feather.<br>
<b>Fallback:</b> Auto-switches to Hybrid if AI produces poor results.</p>
        """)
        mode_layout.addWidget(mode_a_desc)

        # Mode B
        self.mode_b_radio = QRadioButton("Mode B: Classical-first + AI fallback")
        self.mode_b_radio.setToolTip(
            "Classical segmentation (Lab distance + GrabCut) first. "
            "Falls back to AI if QC fails."
        )
        self.mode_group.addButton(self.mode_b_radio, 1)
        mode_layout.addWidget(self.mode_b_radio)

        mode_b_desc = QTextEdit()
        mode_b_desc.setReadOnly(True)
        mode_b_desc.setMaximumHeight(60)
        mode_b_desc.setHtml("""
<p><b>Best for:</b> Simple backgrounds, faster processing on easy images.<br>
<b>Process:</b> Classical → QC check → AI fallback if needed.</p>
        """)
        mode_layout.addWidget(mode_b_desc)

        # Mode C
        self.mode_c_radio = QRadioButton("Mode C: Hybrid-merge")
        self.mode_c_radio.setToolTip(
            "Runs both AI and Classical, then merges masks intelligently. "
            "Most robust but slower."
        )
        self.mode_group.addButton(self.mode_c_radio, 2)
        mode_layout.addWidget(self.mode_c_radio)

        mode_c_desc = QTextEdit()
        mode_c_desc.setReadOnly(True)
        mode_c_desc.setMaximumHeight(60)
        mode_c_desc.setHtml("""
<p><b>Best for:</b> Complex/challenging images, maximum quality.<br>
<b>Process:</b> AI + Classical in parallel → Intelligent mask merge → White preservation.</p>
        """)
        mode_layout.addWidget(mode_c_desc)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Force AI option
        force_group = QGroupBox("Override Options")
        force_layout = QVBoxLayout()

        self.force_ai_check = QCheckBox("Force AI for all images (troubleshooting)")
        self.force_ai_check.setToolTip(
            "Override selected mode and use AI segmentation for all images. "
            "Useful for debugging or ensuring consistent AI-based processing."
        )
        self.force_ai_check.setChecked(self.config['processing'].get('force_ai_all', False))

        force_layout.addWidget(self.force_ai_check)
        force_group.setLayout(force_layout)
        layout.addWidget(force_group)

        # Set current mode
        current_mode = self.config['processing'].get('mode', 'A')
        if current_mode == 'A':
            self.mode_a_radio.setChecked(True)
        elif current_mode == 'B':
            self.mode_b_radio.setChecked(True)
        elif current_mode == 'C':
            self.mode_c_radio.setChecked(True)
        else:
            self.mode_a_radio.setChecked(True)  # Default

        layout.addStretch()
        self.setLayout(layout)

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        # Determine selected mode
        if self.mode_a_radio.isChecked():
            mode = 'A'
        elif self.mode_b_radio.isChecked():
            mode = 'B'
        elif self.mode_c_radio.isChecked():
            mode = 'C'
        else:
            mode = 'A'

        return {
            'processing': {
                'mode': mode,
                'force_ai_all': self.force_ai_check.isChecked()
            }
        }
