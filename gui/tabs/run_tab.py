"""
Run tab with progress tracking and controls.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QTextEdit, QLabel, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os


class ProcessingThread(QThread):
    """Background thread for batch processing."""

    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(str)  # csv_path
    error = pyqtSignal(str)  # error_message

    def __init__(self, config, input_folder, output_folder):
        super().__init__()
        self.config = config
        self.input_folder = input_folder
        self.output_folder = output_folder
        self._is_cancelled = False

    def run(self):
        """Run batch processing."""
        try:
            from core.batch_processor import BatchProcessor

            processor = BatchProcessor(self.config)

            # Process with progress callback
            csv_path = processor.process_batch(
                self.input_folder,
                self.output_folder,
                progress_callback=self._progress_callback
            )

            if not self._is_cancelled:
                self.finished.emit(csv_path)

        except Exception as e:
            self.error.emit(str(e))

    def _progress_callback(self, current, total, message):
        """Progress callback."""
        if not self._is_cancelled:
            self.progress.emit(current, total, message)

    def cancel(self):
        """Cancel processing."""
        self._is_cancelled = True


class RunTab(QWidget):
    """Run tab widget."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.processing_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Control buttons group
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Processing")
        self.start_btn.setStyleSheet(
            "font-weight: bold; padding: 10px; background-color: #4CAF50; color: white;"
        )
        self.start_btn.clicked.connect(self.start_processing)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_processing)

        self.open_output_btn = QPushButton("Open Output Folder")
        self.open_output_btn.clicked.connect(self.open_output_folder)

        self.open_csv_btn = QPushButton("Open CSV Report")
        self.open_csv_btn.setEnabled(False)
        self.open_csv_btn.clicked.connect(self.open_csv_report)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.cancel_btn)
        control_layout.addWidget(self.open_output_btn)
        control_layout.addWidget(self.open_csv_btn)
        control_layout.addStretch()

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Progress group
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()

        self.progress_label = QLabel("Ready to process")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Log group
        log_group = QGroupBox("Processing Log")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText(
            "Processing log will appear here.\n\n"
            "Format: # | filename | Mode | Model | FG% | Edge | time ms | route | ✓/✖"
        )

        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        self.setLayout(layout)

        # Store CSV path
        self.last_csv_path = None

    def start_processing(self):
        """Start batch processing."""
        # Validate configuration
        input_folder = self.config['input'].get('source_folder', '')
        output_folder = self.config['output'].get('output_folder', '')

        if not input_folder or not os.path.isdir(input_folder):
            self.log("Error: Invalid input folder. Please configure in Input tab.")
            return

        if not output_folder:
            self.log("Error: Output folder not specified. Please configure in Output tab.")
            return

        if os.path.normpath(input_folder) == os.path.normpath(output_folder):
            self.log("Error: Output folder must be different from input folder.")
            return

        # Create output folder if needed
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            self.log(f"Error creating output folder: {e}")
            return

        # Clear log
        self.log_text.clear()
        self.log("Starting batch processing...")
        self.log(f"Input: {input_folder}")
        self.log(f"Output: {output_folder}")
        self.log(f"Mode: {self.config['processing']['mode']}")
        self.log(f"Model: {self.config['model']['ai_model']}")
        self.log("")

        # Disable start button, enable cancel
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.open_csv_btn.setEnabled(False)

        # Start processing thread
        self.processing_thread = ProcessingThread(self.config, input_folder, output_folder)
        self.processing_thread.progress.connect(self.on_progress)
        self.processing_thread.finished.connect(self.on_finished)
        self.processing_thread.error.connect(self.on_error)
        self.processing_thread.start()

    def cancel_processing(self):
        """Cancel processing."""
        if self.processing_thread:
            self.log("Cancelling processing...")
            self.processing_thread.cancel()
            self.processing_thread.wait()
            self.log("Processing cancelled.")

            self.start_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)

    def on_progress(self, current, total, message):
        """Handle progress update."""
        # Update progress bar
        progress_pct = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress_pct)

        # Update label
        self.progress_label.setText(f"Processing: {current}/{total} ({progress_pct}%)")

        # Log message
        self.log(message)

    def on_finished(self, csv_path):
        """Handle processing finished."""
        self.log("")
        self.log("=" * 60)
        self.log("Processing complete!")
        self.log(f"CSV report: {csv_path}")
        self.log("=" * 60)

        self.progress_label.setText("Processing complete!")
        self.progress_bar.setValue(100)

        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_csv_btn.setEnabled(True)

        # Store CSV path
        self.last_csv_path = csv_path

    def on_error(self, error_msg):
        """Handle processing error."""
        self.log("")
        self.log(f"ERROR: {error_msg}")

        self.progress_label.setText("Error occurred!")

        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def log(self, message):
        """Append message to log."""
        self.log_text.append(message)

        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def open_output_folder(self):
        """Open output folder in file manager."""
        output_folder = self.config['output'].get('output_folder', '')

        if output_folder and os.path.isdir(output_folder):
            import subprocess
            import platform

            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(output_folder)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", output_folder])
                else:  # Linux
                    subprocess.run(["xdg-open", output_folder])
            except Exception as e:
                self.log(f"Could not open folder: {e}")
        else:
            self.log("Output folder not set or doesn't exist.")

    def open_csv_report(self):
        """Open CSV report in default application."""
        if self.last_csv_path and os.path.isfile(self.last_csv_path):
            import subprocess
            import platform

            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(self.last_csv_path)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", self.last_csv_path])
                else:  # Linux
                    subprocess.run(["xdg-open", self.last_csv_path])
            except Exception as e:
                self.log(f"Could not open CSV: {e}")
        else:
            self.log("No CSV report available yet.")
