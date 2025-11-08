"""
Main application window.
"""
import os
import yaml
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMenuBar, QMenu, QAction, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

from gui.tabs.input_tab import InputTab
from gui.tabs.output_tab import OutputTab
from gui.tabs.mode_tab import ModeTab
from gui.tabs.model_tab import ModelTab
from gui.tabs.cpg_tab import CPGTab
from gui.tabs.qc_tab import QCTab
from gui.tabs.performance_tab import PerformanceTab
from gui.tabs.run_tab import RunTab


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.config_path = "config.yaml"
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle("Background Remover - White Product Edition")
        self.setGeometry(100, 100, 900, 700)

        # Create menu bar
        self.create_menu()

        # Create central widget with tabs
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create tab widget
        self.tabs = QTabWidget()

        # Add tabs
        self.input_tab = InputTab(self.config)
        self.output_tab = OutputTab(self.config)
        self.mode_tab = ModeTab(self.config)
        self.cpg_tab = CPGTab(self.config)
        self.model_tab = ModelTab(self.config)
        self.qc_tab = QCTab(self.config)
        self.performance_tab = PerformanceTab(self.config)
        self.run_tab = RunTab(self.config)

        self.tabs.addTab(self.input_tab, "1. Input")
        self.tabs.addTab(self.output_tab, "2. Output & Naming")
        self.tabs.addTab(self.mode_tab, "3. Processing Mode")
        self.tabs.addTab(self.cpg_tab, "4. CPG Presets")
        self.tabs.addTab(self.model_tab, "5. Model & Refinement")
        self.tabs.addTab(self.qc_tab, "6. QC & Logging")
        self.tabs.addTab(self.performance_tab, "7. Performance")
        self.tabs.addTab(self.run_tab, "8. Run")

        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Set default tab
        self.tabs.setCurrentIndex(0)

    def create_menu(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        load_action = QAction("Load Config...", self)
        load_action.triggered.connect(self.load_config_dialog)
        file_menu.addAction(load_action)

        save_action = QAction("Save Config", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Config As...", self)
        save_as_action.triggered.connect(self.save_config_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def load_config(self):
        """Load configuration from YAML."""
        config_path = "config.yaml"

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                return config
            except Exception as e:
                print(f"Error loading config: {e}")

        # Return default config
        return self.get_default_config()

    def get_default_config(self):
        """Get default configuration."""
        return {
            'input': {
                'source_folder': '',
                'extensions': ['jpg', 'jpeg', 'png', 'webp'],
                'recursive': True
            },
            'output': {
                'output_folder': '',
                'overwrite_policy': 'disambiguate'
            },
            'processing': {
                'mode': 'A',
                'force_ai_all': False
            },
            'cpg': {
                'preset_enabled': False,
                'preset_name': 'none'
            },
            'model': {
                'ai_model': 'isnet-general'
            },
            'refinement': {
                'edge_feather_px': 3,
                'grabcut_enabled': True,
                'grabcut_iterations': 4,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 25,
                    'hsv_v_threshold': 220,
                    'lab_l_threshold': 85
                },
                'trimming': {
                    'enabled': True,
                    'safe_margin_px': 3
                }
            },
            'qc': {
                'fg_ratio_min': 10,
                'fg_ratio_max': 90,
                'edge_confidence_min': 14,
                'fallback_fg_ratio_min': 8,
                'fallback_fg_ratio_max': 95,
                'fallback_edge_confidence_min': 12
            },
            'logging': {
                'csv_enabled': True,
                'debug_masks_enabled': False
            },
            'performance': {
                'concurrency': 'auto',
                'max_side_px': 1800,
                'timeout_ai_ms': 12000,
                'timeout_classical_ms': 4000,
                'queue_order': 'natural'
            }
        }

    def update_config_from_tabs(self):
        """Update config from all tabs."""
        # Get updates from each tab
        tabs = [
            self.input_tab,
            self.output_tab,
            self.mode_tab,
            self.cpg_tab,
            self.model_tab,
            self.qc_tab,
            self.performance_tab
        ]

        for tab in tabs:
            updates = tab.get_config_updates()
            for key, value in updates.items():
                if isinstance(value, dict):
                    if key not in self.config:
                        self.config[key] = {}
                    self.config[key].update(value)
                else:
                    self.config[key] = value

    def save_config(self):
        """Save configuration to YAML."""
        self.update_config_from_tabs()

        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

            QMessageBox.information(
                self,
                "Config Saved",
                f"Configuration saved to {self.config_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save config: {e}"
            )

    def save_config_as(self):
        """Save configuration to custom file."""
        self.update_config_from_tabs()

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "YAML Files (*.yaml *.yml)"
        )

        if filepath:
            try:
                with open(filepath, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

                self.config_path = filepath
                QMessageBox.information(
                    self,
                    "Config Saved",
                    f"Configuration saved to {filepath}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save config: {e}"
                )

    def load_config_dialog(self):
        """Load configuration from file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "YAML Files (*.yaml *.yml)"
        )

        if filepath:
            try:
                with open(filepath, 'r') as f:
                    self.config = yaml.safe_load(f)

                self.config_path = filepath

                # Refresh all tabs
                # (Simple approach: recreate tabs)
                QMessageBox.information(
                    self,
                    "Config Loaded",
                    f"Configuration loaded. Please restart the application to apply changes."
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load config: {e}"
                )

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Background Remover",
            "<h2>Background Remover</h2>"
            "<p><b>Version:</b> 1.0</p>"
            "<p><b>Purpose:</b> Remove backgrounds from white/near-white product images</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>AI-based segmentation (isnet-general, u2net, u2netp)</li>"
            "<li>Classical segmentation (Lab distance, GrabCut)</li>"
            "<li>White preservation for white-on-white products</li>"
            "<li>Three processing modes: AI-first, Classical-first, Hybrid</li>"
            "<li>Batch processing with concurrency</li>"
            "<li>CSV reporting and QC metrics</li>"
            "</ul>"
            "<p><b>Output:</b> PNG RGBA with orientation suffixes (_PRT, _LSC, _SQR_LSC)</p>"
        )

    def closeEvent(self, event):
        """Handle window close."""
        # Save config on exit
        self.update_config_from_tabs()
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except:
            pass

        event.accept()
