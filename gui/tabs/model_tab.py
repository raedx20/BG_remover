"""
Model & Refinement tab.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QCheckBox, QGroupBox
)


class ModelTab(QWidget):
    """Model & Refinement tab widget."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # AI Model selection group
        model_group = QGroupBox("AI Model")
        model_layout = QVBoxLayout()

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))

        self.model_combo = QComboBox()
        # All available rembg models
        self.model_combo.addItem("isnet-general (Default - Products, 176MB)", "isnet-general")
        self.model_combo.addItem("u2net (General purpose, 176MB)", "u2net")
        self.model_combo.addItem("u2netp (Lightweight/fast, 4.7MB)", "u2netp")
        self.model_combo.addItem("u2net-human (People/portraits, 176MB)", "u2net-human")
        self.model_combo.addItem("u2net-cloth (Clothing/fashion, 176MB)", "u2net-cloth")
        self.model_combo.addItem("silueta (Silhouettes, 43MB)", "silueta")
        self.model_combo.addItem("isnet-anime (Anime/illustrations, 176MB)", "isnet-anime")
        self.model_combo.addItem("sam (Segment Anything, 358MB)", "sam")

        # Set current value
        current_model = self.config['model'].get('ai_model', 'isnet-general')
        index = self.model_combo.findData(current_model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)

        model_row.addWidget(self.model_combo)
        model_row.addStretch()
        model_layout.addLayout(model_row)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Alpha Matting group (rembg native feature)
        alpha_matting_group = QGroupBox("Alpha Matting (rembg Feature)")
        alpha_matting_layout = QVBoxLayout()

        self.alpha_matting_check = QCheckBox("Enable alpha matting")
        alpha_matting_cfg = self.config['model'].get('alpha_matting', {})
        self.alpha_matting_check.setChecked(alpha_matting_cfg.get('enabled', False))
        self.alpha_matting_check.setToolTip(
            "Enable alpha matting for better edge quality on complex/hairy edges.\n"
            "Slower but produces smoother, more accurate edges. Good for products with fur, hair, or fine details."
        )
        alpha_matting_layout.addWidget(self.alpha_matting_check)

        # FG threshold
        fg_thresh_row = QHBoxLayout()
        fg_thresh_row.addWidget(QLabel("    Foreground threshold:"))
        self.alpha_fg_spin = QSpinBox()
        self.alpha_fg_spin.setRange(0, 255)
        self.alpha_fg_spin.setValue(alpha_matting_cfg.get('foreground_threshold', 240))
        self.alpha_fg_spin.setToolTip("Higher = stricter foreground detection (default: 240)")
        fg_thresh_row.addWidget(self.alpha_fg_spin)
        fg_thresh_row.addStretch()
        alpha_matting_layout.addLayout(fg_thresh_row)

        # BG threshold
        bg_thresh_row = QHBoxLayout()
        bg_thresh_row.addWidget(QLabel("    Background threshold:"))
        self.alpha_bg_spin = QSpinBox()
        self.alpha_bg_spin.setRange(0, 255)
        self.alpha_bg_spin.setValue(alpha_matting_cfg.get('background_threshold', 10))
        self.alpha_bg_spin.setToolTip("Lower = stricter background detection (default: 10)")
        bg_thresh_row.addWidget(self.alpha_bg_spin)
        bg_thresh_row.addStretch()
        alpha_matting_layout.addLayout(bg_thresh_row)

        # Erode size
        erode_row = QHBoxLayout()
        erode_row.addWidget(QLabel("    Erode size:"))
        self.alpha_erode_spin = QSpinBox()
        self.alpha_erode_spin.setRange(1, 30)
        self.alpha_erode_spin.setValue(alpha_matting_cfg.get('erode_size', 10))
        self.alpha_erode_spin.setToolTip("Erosion kernel size for matting (default: 10)")
        erode_row.addWidget(self.alpha_erode_spin)
        erode_row.addStretch()
        alpha_matting_layout.addLayout(erode_row)

        # Post-process mask
        self.post_process_check = QCheckBox("Apply rembg post-processing")
        self.post_process_check.setChecked(self.config['model'].get('post_process_mask', False))
        self.post_process_check.setToolTip(
            "Apply rembg's built-in morphological post-processing to the mask.\n"
            "Helps clean up noise and smooth edges."
        )
        alpha_matting_layout.addWidget(self.post_process_check)

        alpha_matting_group.setLayout(alpha_matting_layout)
        layout.addWidget(alpha_matting_group)

        # Refinement settings group
        refine_group = QGroupBox("Refinement Settings")
        refine_layout = QVBoxLayout()

        # Edge feather
        feather_row = QHBoxLayout()
        feather_row.addWidget(QLabel("Edge feather (pixels):"))
        self.feather_spin = QSpinBox()
        self.feather_spin.setRange(0, 10)
        self.feather_spin.setValue(self.config['refinement'].get('edge_feather_px', 3))
        self.feather_spin.setToolTip("Softens edges for smoother transitions. 0 = no feathering.")
        feather_row.addWidget(self.feather_spin)
        feather_row.addStretch()
        refine_layout.addLayout(feather_row)

        # GrabCut enabled
        self.grabcut_check = QCheckBox("Enable GrabCut refinement")
        self.grabcut_check.setChecked(self.config['refinement'].get('grabcut_enabled', True))
        self.grabcut_check.setToolTip("Refine AI mask using GrabCut algorithm (recommended).")
        refine_layout.addWidget(self.grabcut_check)

        # GrabCut iterations
        grabcut_iter_row = QHBoxLayout()
        grabcut_iter_row.addWidget(QLabel("    GrabCut iterations:"))
        self.grabcut_iter_spin = QSpinBox()
        self.grabcut_iter_spin.setRange(1, 10)
        self.grabcut_iter_spin.setValue(self.config['refinement'].get('grabcut_iterations', 4))
        self.grabcut_iter_spin.setToolTip("Number of GrabCut iterations. 3-5 recommended.")
        grabcut_iter_row.addWidget(self.grabcut_iter_spin)
        grabcut_iter_row.addStretch()
        refine_layout.addLayout(grabcut_iter_row)

        refine_group.setLayout(refine_layout)
        layout.addWidget(refine_group)

        # White preservation group (always on)
        white_group = QGroupBox("White Preservation (Always Enabled)")
        white_layout = QVBoxLayout()

        white_desc = QLabel(
            "Preserves low-saturation, high-luminance pixels inside the product mask.\n"
            "Critical for white-on-white products (labels, caps, highlights)."
        )
        white_desc.setWordWrap(True)
        white_desc.setStyleSheet("color: #333;")
        white_layout.addWidget(white_desc)

        # HSV thresholds
        hsv_row1 = QHBoxLayout()
        hsv_row1.addWidget(QLabel("HSV Saturation threshold (S ≤):"))
        self.hsv_s_spin = QSpinBox()
        self.hsv_s_spin.setRange(0, 100)
        self.hsv_s_spin.setValue(
            self.config['refinement']['white_preservation'].get('hsv_s_threshold', 25)
        )
        hsv_row1.addWidget(self.hsv_s_spin)
        hsv_row1.addStretch()
        white_layout.addLayout(hsv_row1)

        hsv_row2 = QHBoxLayout()
        hsv_row2.addWidget(QLabel("HSV Value threshold (V ≥):"))
        self.hsv_v_spin = QSpinBox()
        self.hsv_v_spin.setRange(0, 255)
        self.hsv_v_spin.setValue(
            self.config['refinement']['white_preservation'].get('hsv_v_threshold', 220)
        )
        hsv_row2.addWidget(self.hsv_v_spin)
        hsv_row2.addStretch()
        white_layout.addLayout(hsv_row2)

        # Lab threshold
        lab_row = QHBoxLayout()
        lab_row.addWidget(QLabel("Lab Lightness threshold (L ≥):"))
        self.lab_l_spin = QSpinBox()
        self.lab_l_spin.setRange(0, 100)
        self.lab_l_spin.setValue(
            self.config['refinement']['white_preservation'].get('lab_l_threshold', 85)
        )
        lab_row.addWidget(self.lab_l_spin)
        lab_row.addStretch()
        white_layout.addLayout(lab_row)

        white_group.setLayout(white_layout)
        layout.addWidget(white_group)

        # Trimming group
        trim_group = QGroupBox("Trimming")
        trim_layout = QVBoxLayout()

        self.trim_check = QCheckBox("Enable automatic trimming")
        self.trim_check.setChecked(self.config['refinement']['trimming'].get('enabled', True))
        self.trim_check.setToolTip("Remove transparent borders from output images.")
        trim_layout.addWidget(self.trim_check)

        trim_margin_row = QHBoxLayout()
        trim_margin_row.addWidget(QLabel("    Safe margin (pixels):"))
        self.trim_margin_spin = QSpinBox()
        self.trim_margin_spin.setRange(0, 20)
        self.trim_margin_spin.setValue(
            self.config['refinement']['trimming'].get('safe_margin_px', 3)
        )
        self.trim_margin_spin.setToolTip("Margin to keep around trimmed content (2-4 recommended).")
        trim_margin_row.addWidget(self.trim_margin_spin)
        trim_margin_row.addStretch()
        trim_layout.addLayout(trim_margin_row)

        trim_group.setLayout(trim_layout)
        layout.addWidget(trim_group)

        layout.addStretch()
        self.setLayout(layout)

    def get_config_updates(self):
        """Get configuration updates from this tab."""
        return {
            'model': {
                'ai_model': self.model_combo.currentData(),
                'alpha_matting': {
                    'enabled': self.alpha_matting_check.isChecked(),
                    'foreground_threshold': self.alpha_fg_spin.value(),
                    'background_threshold': self.alpha_bg_spin.value(),
                    'erode_size': self.alpha_erode_spin.value()
                },
                'post_process_mask': self.post_process_check.isChecked()
            },
            'refinement': {
                'edge_feather_px': self.feather_spin.value(),
                'grabcut_enabled': self.grabcut_check.isChecked(),
                'grabcut_iterations': self.grabcut_iter_spin.value(),
                'white_preservation': {
                    'enabled': True,  # Always on
                    'hsv_s_threshold': self.hsv_s_spin.value(),
                    'hsv_v_threshold': self.hsv_v_spin.value(),
                    'lab_l_threshold': self.lab_l_spin.value()
                },
                'trimming': {
                    'enabled': self.trim_check.isChecked(),
                    'safe_margin_px': self.trim_margin_spin.value()
                }
            }
        }
