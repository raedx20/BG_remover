"""
CPG (Consumer Packaged Goods) Presets tab.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QGroupBox, QTextEdit, QPushButton
)
from PyQt5.QtCore import pyqtSignal

from core.cpg_presets import list_cpg_presets, CPG_QUICK_GUIDE


class CPGTab(QWidget):
    """CPG Presets tab widget."""

    preset_changed = pyqtSignal(str)  # Signal when preset is selected

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.cpg_presets = list_cpg_presets()
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # CPG Enable group
        enable_group = QGroupBox("CPG Product Optimization")
        enable_layout = QVBoxLayout()

        self.cpg_enable_check = QCheckBox("Enable CPG Preset (overrides manual settings)")
        cpg_cfg = self.config.get('cpg', {})
        self.cpg_enable_check.setChecked(cpg_cfg.get('preset_enabled', False))
        self.cpg_enable_check.setToolTip(
            "Enable to use optimized settings for CPG (Consumer Packaged Goods) products.\n"
            "When enabled, preset settings override manual Model & Refinement tab settings."
        )
        self.cpg_enable_check.stateChanged.connect(self.on_enable_changed)
        enable_layout.addWidget(self.cpg_enable_check)

        enable_group.setLayout(enable_layout)
        layout.addWidget(enable_group)

        # Preset selection group
        preset_group = QGroupBox("Product Type")
        preset_layout = QVBoxLayout()

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Select CPG Product Type:"))

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Select Product Type --", "none")

        # Add all CPG presets
        for key, info in self.cpg_presets.items():
            display_name = f"{info['name']}"
            self.preset_combo.addItem(display_name, key)

        # Set current value
        current_preset = cpg_cfg.get('preset_name', 'none')
        index = self.preset_combo.findData(current_preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)

        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_row.addWidget(self.preset_combo)
        preset_row.addStretch()
        preset_layout.addLayout(preset_row)

        # Description display
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(120)
        preset_layout.addWidget(QLabel("Description:"))
        preset_layout.addWidget(self.description_text)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Quick reference guide
        guide_group = QGroupBox("Quick Reference Guide")
        guide_layout = QVBoxLayout()

        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.guide_text.setPlainText(CPG_QUICK_GUIDE)
        self.guide_text.setMaximumHeight(300)

        guide_layout.addWidget(self.guide_text)
        guide_group.setLayout(guide_layout)
        layout.addWidget(guide_group)

        # Info label
        info_label = QLabel(
            "<b>Note:</b> When CPG preset is enabled, it will automatically configure:\n"
            "• Best AI model for the product type\n"
            "• Optimal alpha matting settings\n"
            "• Processing mode (A/B/C)\n"
            "• White preservation thresholds\n"
            "• Refinement settings"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #f0f8ff; border: 1px solid #ccc;")
        layout.addWidget(info_label)

        layout.addStretch()
        self.setLayout(layout)

        # Update description initially
        self.update_description()

    def on_enable_changed(self, state):
        """Handle enable checkbox state change."""
        enabled = state == 2  # Qt.Checked
        self.preset_combo.setEnabled(enabled)

    def on_preset_changed(self, index):
        """Handle preset selection change."""
        self.update_description()

        # Emit signal
        preset_name = self.preset_combo.currentData()
        self.preset_changed.emit(preset_name)

    def update_description(self):
        """Update description text based on selected preset."""
        preset_name = self.preset_combo.currentData()

        if preset_name == "none":
            self.description_text.setPlainText(
                "No preset selected. Use manual settings from Model & Refinement tab."
            )
            return

        preset_info = self.cpg_presets.get(preset_name, {})

        if preset_info:
            description = f"""
<b>Product Type:</b> {preset_info['name']}

<b>Description:</b> {preset_info['description']}

<b>Examples:</b> {preset_info['examples']}

<b>Recommended Model:</b> {preset_info['recommended_model']}

<b>Optimizations:</b>
• Configured for this specific CPG category
• Balanced quality vs. speed for production use
• Tested on real-world product images
            """.strip()

            self.description_text.setHtml(description)
        else:
            self.description_text.setPlainText("Preset information not available.")

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        return {
            'cpg': {
                'preset_enabled': self.cpg_enable_check.isChecked(),
                'preset_name': self.preset_combo.currentData()
            }
        }
