"""
Batch processing with concurrency and CSV reporting.
"""
import os
import csv
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
import multiprocessing

from core.processor import ImageProcessor
from core.utils import scan_images


class BatchProcessor:
    """Batch processor for multiple images with CSV reporting."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize batch processor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.processor = ImageProcessor(config)
        self.results = []

    def process_batch(self, input_folder: str, output_folder: str,
                     progress_callback: Callable[[int, int, str], None] = None) -> str:
        """
        Process batch of images.

        Args:
            input_folder: Input folder path
            output_folder: Output folder path
            progress_callback: Optional callback(current, total, message)

        Returns:
            Path to CSV report
        """
        # Scan images
        image_files = scan_images(
            input_folder,
            self.config['input']['extensions'],
            self.config['input']['recursive']
        )

        if not image_files:
            raise ValueError(f"No images found in {input_folder}")

        total = len(image_files)

        # Apply queue order
        queue_order = self.config['performance']['queue_order']
        if queue_order == 'smallest_first':
            image_files = self._sort_by_size(image_files)

        # Create output folder
        os.makedirs(output_folder, exist_ok=True)

        # Determine concurrency
        concurrency = self._get_concurrency()

        # Process images
        self.results = []

        if concurrency == 1:
            # Sequential processing
            for idx, image_path in enumerate(image_files):
                if progress_callback:
                    progress_callback(idx, total, f"Processing {os.path.basename(image_path)}")

                result = self.processor.process_image(image_path, output_folder)
                self.results.append(result)

                if progress_callback:
                    status_icon = "✓" if result['status'] == 'success' else "✖"
                    progress_callback(
                        idx + 1, total,
                        f"{status_icon} {os.path.basename(image_path)} | "
                        f"Mode {result.get('mode', 'N/A')} | "
                        f"FG {result.get('fg_ratio', 0):.1f}% | "
                        f"{result.get('elapsed_ms', 0)} ms"
                    )
        else:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                # Submit all tasks
                future_to_path = {
                    executor.submit(self.processor.process_image, img_path, output_folder): img_path
                    for img_path in image_files
                }

                completed = 0
                for future in as_completed(future_to_path):
                    img_path = future_to_path[future]
                    result = future.result()
                    self.results.append(result)

                    completed += 1
                    if progress_callback:
                        status_icon = "✓" if result['status'] == 'success' else "✖"
                        progress_callback(
                            completed, total,
                            f"{status_icon} {os.path.basename(img_path)} | "
                            f"Mode {result.get('mode', 'N/A')} | "
                            f"FG {result.get('fg_ratio', 0):.1f}% | "
                            f"{result.get('elapsed_ms', 0)} ms"
                        )

        # Generate CSV report
        csv_path = self._write_csv_report(output_folder)

        return csv_path

    def _get_concurrency(self) -> int:
        """Get concurrency level."""
        concurrency = self.config['performance']['concurrency']

        if concurrency == 'auto':
            # Use CPU count
            return max(1, multiprocessing.cpu_count() - 1)
        else:
            return max(1, int(concurrency))

    def _sort_by_size(self, image_files: List[str]) -> List[str]:
        """Sort images by file size (smallest first)."""
        return sorted(image_files, key=lambda x: os.path.getsize(x))

    def _write_csv_report(self, output_folder: str) -> str:
        """
        Write CSV report.

        Args:
            output_folder: Output folder path

        Returns:
            Path to CSV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"bg_removal_report_{timestamp}.csv"
        csv_path = os.path.join(output_folder, csv_filename)

        # CSV columns
        fieldnames = [
            'input_path',
            'output_path',
            'mode',
            'model',
            'fg_ratio',
            'edge_conf',
            'elapsed_ms',
            'status',
            'notes'
        ]

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                writer.writerow({
                    'input_path': result.get('input_path', ''),
                    'output_path': result.get('output_path', ''),
                    'mode': result.get('mode', ''),
                    'model': result.get('model', ''),
                    'fg_ratio': f"{result.get('fg_ratio', 0):.2f}",
                    'edge_conf': f"{result.get('edge_conf', 0):.2f}",
                    'elapsed_ms': result.get('elapsed_ms', 0),
                    'status': result.get('status', 'unknown'),
                    'notes': result.get('notes', '')
                })

        return csv_path

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics from batch processing.

        Returns:
            Dictionary with summary stats
        """
        if not self.results:
            return {}

        total = len(self.results)
        success = sum(1 for r in self.results if r['status'] == 'success')
        failed = total - success

        total_time = sum(r.get('elapsed_ms', 0) for r in self.results)
        avg_time = total_time / total if total > 0 else 0

        return {
            'total': total,
            'success': success,
            'failed': failed,
            'total_time_ms': total_time,
            'avg_time_ms': avg_time
        }
