"""
QC & Logging tab.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QGroupBox, QTextEdit
)


class QCTab(QWidget):
    """QC & Logging tab widget."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # QC Metrics group
        qc_group = QGroupBox("Quality Control Metrics")
        qc_layout = QVBoxLayout()

        qc_desc = QLabel(
            "These metrics are used to detect potential issues and trigger fallbacks.\n"
            "Warnings are informational only - they won't reject white products."
        )
        qc_desc.setWordWrap(True)
        qc_desc.setStyleSheet("color: #333; margin-bottom: 10px;")
        qc_layout.addWidget(qc_desc)

        # FG ratio range
        fg_row1 = QHBoxLayout()
        fg_row1.addWidget(QLabel("Expected FG ratio min (%):"))
        self.fg_min_spin = QSpinBox()
        self.fg_min_spin.setRange(0, 100)
        self.fg_min_spin.setValue(self.config['qc'].get('fg_ratio_min', 10))
        self.fg_min_spin.setToolTip("Minimum expected foreground percentage (warning level).")
        fg_row1.addWidget(self.fg_min_spin)
        fg_row1.addStretch()
        qc_layout.addLayout(fg_row1)

        fg_row2 = QHBoxLayout()
        fg_row2.addWidget(QLabel("Expected FG ratio max (%):"))
        self.fg_max_spin = QSpinBox()
        self.fg_max_spin.setRange(0, 100)
        self.fg_max_spin.setValue(self.config['qc'].get('fg_ratio_max', 90))
        self.fg_max_spin.setToolTip("Maximum expected foreground percentage (warning level).")
        fg_row2.addWidget(self.fg_max_spin)
        fg_row2.addStretch()
        qc_layout.addLayout(fg_row2)

        # Edge confidence
        edge_row = QHBoxLayout()
        edge_row.addWidget(QLabel("Edge confidence min:"))
        self.edge_min_spin = QSpinBox()
        self.edge_min_spin.setRange(0, 100)
        self.edge_min_spin.setValue(self.config['qc'].get('edge_confidence_min', 14))
        self.edge_min_spin.setToolTip("Minimum Laplacian median for edge quality (warning level).")
        edge_row.addWidget(self.edge_min_spin)
        edge_row.addStretch()
        qc_layout.addLayout(edge_row)

        qc_group.setLayout(qc_layout)
        layout.addWidget(qc_group)

        # Fallback thresholds group (Mode A only)
        fallback_group = QGroupBox("Fallback Thresholds (Mode A Only)")
        fallback_layout = QVBoxLayout()

        fallback_desc = QLabel(
            "In Mode A, if these stricter thresholds aren't met, "
            "processing automatically switches to Hybrid mode for better results."
        )
        fallback_desc.setWordWrap(True)
        fallback_desc.setStyleSheet("color: #333; margin-bottom: 10px;")
        fallback_layout.addWidget(fallback_desc)

        # Fallback FG ratio
        fb_fg_row1 = QHBoxLayout()
        fb_fg_row1.addWidget(QLabel("Fallback FG ratio min (%):"))
        self.fb_fg_min_spin = QSpinBox()
        self.fb_fg_min_spin.setRange(0, 100)
        self.fb_fg_min_spin.setValue(self.config['qc'].get('fallback_fg_ratio_min', 8))
        fb_fg_row1.addWidget(self.fb_fg_min_spin)
        fb_fg_row1.addStretch()
        fallback_layout.addLayout(fb_fg_row1)

        fb_fg_row2 = QHBoxLayout()
        fb_fg_row2.addWidget(QLabel("Fallback FG ratio max (%):"))
        self.fb_fg_max_spin = QSpinBox()
        self.fb_fg_max_spin.setRange(0, 100)
        self.fb_fg_max_spin.setValue(self.config['qc'].get('fallback_fg_ratio_max', 95))
        fb_fg_row2.addWidget(self.fb_fg_max_spin)
        fb_fg_row2.addStretch()
        fallback_layout.addLayout(fb_fg_row2)

        # Fallback edge confidence
        fb_edge_row = QHBoxLayout()
        fb_edge_row.addWidget(QLabel("Fallback edge confidence min:"))
        self.fb_edge_min_spin = QSpinBox()
        self.fb_edge_min_spin.setRange(0, 100)
        self.fb_edge_min_spin.setValue(self.config['qc'].get('fallback_edge_confidence_min', 12))
        fb_edge_row.addWidget(self.fb_edge_min_spin)
        fb_edge_row.addStretch()
        fallback_layout.addLayout(fb_edge_row)

        fallback_group.setLayout(fallback_layout)
        layout.addWidget(fallback_group)

        # Logging options group
        logging_group = QGroupBox("Logging Options")
        logging_layout = QVBoxLayout()

        # CSV (always on)
        csv_label = QLabel("✓ CSV reporting is always enabled")
        csv_label.setStyleSheet("color: green; font-weight: bold;")
        logging_layout.addWidget(csv_label)

        csv_desc = QTextEdit()
        csv_desc.setReadOnly(True)
        csv_desc.setMaximumHeight(80)
        csv_desc.setHtml("""
<p>CSV report includes:</p>
<ul>
<li>Input/output paths</li>
<li>Processing mode and model used</li>
<li>QC metrics (FG ratio, edge confidence)</li>
<li>Processing time and status</li>
<li>Notes and warnings</li>
</ul>
        """)
        logging_layout.addWidget(csv_desc)

        # Debug masks toggle
        self.debug_masks_check = QCheckBox("Enable debug mask export (side-by-side previews)")
        self.debug_masks_check.setChecked(
            self.config['logging'].get('debug_masks_enabled', False)
        )
        self.debug_masks_check.setToolTip(
            "Save small side-by-side previews showing original, AI mask, and final alpha. "
            "Useful for troubleshooting. OFF by default."
        )
        logging_layout.addWidget(self.debug_masks_check)

        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)

        layout.addStretch()
        self.setLayout(layout)

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        return {
            'qc': {
                'fg_ratio_min': self.fg_min_spin.value(),
                'fg_ratio_max': self.fg_max_spin.value(),
                'edge_confidence_min': self.edge_min_spin.value(),
                'fallback_fg_ratio_min': self.fb_fg_min_spin.value(),
                'fallback_fg_ratio_max': self.fb_fg_max_spin.value(),
                'fallback_edge_confidence_min': self.fb_edge_min_spin.value()
            },
            'logging': {
                'csv_enabled': True,  # Always on
                'debug_masks_enabled': self.debug_masks_check.isChecked()
            }
        }
