"""
Performance tab.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QComboBox, QGroupBox, QRadioButton, QButtonGroup
)
import multiprocessing


class PerformanceTab(QWidget):
    """Performance tab widget."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Concurrency group
        concurrency_group = QGroupBox("Concurrency")
        concurrency_layout = QVBoxLayout()

        self.concurrency_group = QButtonGroup()

        # Auto mode
        self.auto_radio = QRadioButton("Auto (CPU-based)")
        self.auto_radio.setToolTip(
            f"Automatically use {max(1, multiprocessing.cpu_count() - 1)} threads "
            f"based on available CPU cores."
        )
        self.concurrency_group.addButton(self.auto_radio, 0)
        concurrency_layout.addWidget(self.auto_radio)

        # Fixed mode
        fixed_row = QHBoxLayout()
        self.fixed_radio = QRadioButton("Fixed:")
        self.concurrency_group.addButton(self.fixed_radio, 1)
        fixed_row.addWidget(self.fixed_radio)

        self.fixed_spin = QSpinBox()
        self.fixed_spin.setRange(1, 32)
        self.fixed_spin.setValue(4)
        self.fixed_spin.setToolTip("Number of concurrent processing threads.")
        fixed_row.addWidget(self.fixed_spin)
        fixed_row.addWidget(QLabel("threads"))
        fixed_row.addStretch()
        concurrency_layout.addLayout(fixed_row)

        # Set current value
        current_concurrency = self.config['performance'].get('concurrency', 'auto')
        if current_concurrency == 'auto':
            self.auto_radio.setChecked(True)
        else:
            self.fixed_radio.setChecked(True)
            try:
                self.fixed_spin.setValue(int(current_concurrency))
            except:
                self.fixed_spin.setValue(4)

        concurrency_group.setLayout(concurrency_layout)
        layout.addWidget(concurrency_group)

        # Image sizing group
        sizing_group = QGroupBox("Image Sizing")
        sizing_layout = QVBoxLayout()

        max_side_row = QHBoxLayout()
        max_side_row.addWidget(QLabel("Max side for processing (px):"))
        self.max_side_spin = QSpinBox()
        self.max_side_spin.setRange(512, 4096)
        self.max_side_spin.setSingleStep(100)
        self.max_side_spin.setValue(self.config['performance'].get('max_side_px', 1800))
        self.max_side_spin.setToolTip(
            "Images larger than this will be downscaled for processing, "
            "then output at original size. Range: 1600-2000 recommended."
        )
        max_side_row.addWidget(self.max_side_spin)
        max_side_row.addStretch()
        sizing_layout.addLayout(max_side_row)

        sizing_desc = QLabel(
            "Note: Downscaling improves performance without sacrificing quality. "
            "Final output is saved at original image dimensions."
        )
        sizing_desc.setWordWrap(True)
        sizing_desc.setStyleSheet("color: #666; font-style: italic;")
        sizing_layout.addWidget(sizing_desc)

        sizing_group.setLayout(sizing_layout)
        layout.addWidget(sizing_group)

        # Timeouts group
        timeout_group = QGroupBox("Processing Timeouts")
        timeout_layout = QVBoxLayout()

        ai_timeout_row = QHBoxLayout()
        ai_timeout_row.addWidget(QLabel("AI timeout (ms):"))
        self.ai_timeout_spin = QSpinBox()
        self.ai_timeout_spin.setRange(1000, 60000)
        self.ai_timeout_spin.setSingleStep(1000)
        self.ai_timeout_spin.setValue(self.config['performance'].get('timeout_ai_ms', 12000))
        self.ai_timeout_spin.setToolTip("Maximum time for AI segmentation per image.")
        ai_timeout_row.addWidget(self.ai_timeout_spin)
        ai_timeout_row.addStretch()
        timeout_layout.addLayout(ai_timeout_row)

        classical_timeout_row = QHBoxLayout()
        classical_timeout_row.addWidget(QLabel("Classical timeout (ms):"))
        self.classical_timeout_spin = QSpinBox()
        self.classical_timeout_spin.setRange(1000, 30000)
        self.classical_timeout_spin.setSingleStep(1000)
        self.classical_timeout_spin.setValue(
            self.config['performance'].get('timeout_classical_ms', 4000)
        )
        self.classical_timeout_spin.setToolTip("Maximum time for classical segmentation per image.")
        classical_timeout_row.addWidget(self.classical_timeout_spin)
        classical_timeout_row.addStretch()
        timeout_layout.addLayout(classical_timeout_row)

        timeout_group.setLayout(timeout_layout)
        layout.addWidget(timeout_group)

        # Queue order group
        queue_group = QGroupBox("Queue Order")
        queue_layout = QVBoxLayout()

        self.queue_combo = QComboBox()
        self.queue_combo.addItem("Natural (alphabetical)", "natural")
        self.queue_combo.addItem("Smallest first (by file size)", "smallest_first")

        # Set current value
        current_order = self.config['performance'].get('queue_order', 'natural')
        index = self.queue_combo.findData(current_order)
        if index >= 0:
            self.queue_combo.setCurrentIndex(index)

        queue_layout.addWidget(self.queue_combo)

        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)

        layout.addStretch()
        self.setLayout(layout)

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        # Determine concurrency
        if self.auto_radio.isChecked():
            concurrency = 'auto'
        else:
            concurrency = self.fixed_spin.value()

        return {
            'performance': {
                'concurrency': concurrency,
                'max_side_px': self.max_side_spin.value(),
                'timeout_ai_ms': self.ai_timeout_spin.value(),
                'timeout_classical_ms': self.classical_timeout_spin.value(),
                'queue_order': self.queue_combo.currentData()
            }
        }
