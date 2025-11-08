"""
Main image processor implementing all three modes.
"""
import cv2
import numpy as np
import time
from typing import Dict, Any, Optional, Tuple
from PIL import Image

from core.utils import (
    resize_for_processing,
    upscale_mask,
    trim_transparent_borders,
    save_rgba,
    get_output_path
)
from core.ai_segmentation import (
    segment_with_ai,
    refine_ai_mask_with_grabcut
)
from core.classical_segmentation import segment_with_classical
from core.hybrid import select_best_merge_strategy
from core.white_preservation import (
    apply_white_preservation,
    apply_edge_feather
)
from core.qc_metrics import calculate_qc_metrics, check_qc_thresholds


class ImageProcessor:
    """Main image processor for background removal."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize processor with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def process_image(self, input_path: str, output_folder: str) -> Dict[str, Any]:
        """
        Process single image according to configured mode.

        Args:
            input_path: Input image path
            output_folder: Output folder path

        Returns:
            Processing result dictionary with:
            - status: 'success' or 'failed'
            - output_path: Output file path (if success)
            - mode: Processing mode used
            - model: AI model used (if applicable)
            - fg_ratio: Foreground ratio percentage
            - edge_conf: Edge confidence score
            - elapsed_ms: Processing time in milliseconds
            - notes: Additional notes/warnings
        """
        start_time = time.time()

        try:
            # Load image
            image_bgr = cv2.imread(input_path, cv2.IMREAD_COLOR)
            if image_bgr is None:
                raise ValueError(f"Failed to load image: {input_path}")

            original_shape = image_bgr.shape[:2]  # (h, w)

            # Resize for processing
            max_side = self.config['performance']['max_side_px']
            image_resized, scale = resize_for_processing(image_bgr, max_side)

            # Determine processing mode
            mode = self._get_processing_mode()

            # Process based on mode
            if mode == 'A':
                result = self._process_mode_a(image_resized, input_path)
            elif mode == 'B':
                result = self._process_mode_b(image_resized, input_path)
            elif mode == 'C':
                result = self._process_mode_c(image_resized, input_path)
            else:
                raise ValueError(f"Unknown mode: {mode}")

            alpha_mask = result['alpha_mask']
            processing_notes = result.get('notes', [])

            # Upscale mask to original size if needed
            if scale != 1.0:
                alpha_mask = upscale_mask(alpha_mask, original_shape)

            # Apply trimming
            if self.config['refinement']['trimming']['enabled']:
                margin = self.config['refinement']['trimming']['safe_margin_px']
                image_trimmed, alpha_trimmed = trim_transparent_borders(
                    image_bgr, alpha_mask, margin=margin
                )
            else:
                image_trimmed = image_bgr
                alpha_trimmed = alpha_mask

            # Get output path
            h, w = image_trimmed.shape[:2]
            output_path = get_output_path(
                input_path,
                output_folder,
                self.config['output']['overwrite_policy'],
                w, h
            )

            # Save RGBA PNG
            save_rgba(image_trimmed, alpha_trimmed, output_path)

            # Calculate final QC metrics
            metrics = calculate_qc_metrics(image_trimmed, alpha_trimmed)

            # Calculate elapsed time
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Build result
            return {
                'status': 'success',
                'input_path': input_path,
                'output_path': output_path,
                'mode': mode,
                'model': result.get('model', 'N/A'),
                'fg_ratio': metrics['fg_ratio'],
                'edge_conf': metrics['edge_confidence'],
                'elapsed_ms': elapsed_ms,
                'notes': '; '.join(processing_notes) if processing_notes else ''
            }

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                'status': 'failed',
                'input_path': input_path,
                'output_path': '',
                'mode': '',
                'model': '',
                'fg_ratio': 0.0,
                'edge_conf': 0.0,
                'elapsed_ms': elapsed_ms,
                'notes': str(e)
            }

    def _get_processing_mode(self) -> str:
        """Get effective processing mode."""
        if self.config['processing']['force_ai_all']:
            return 'A'  # Force AI mode
        return self.config['processing']['mode']

    def _process_mode_a(self, image: np.ndarray, input_path: str) -> Dict[str, Any]:
        """
        Mode A: AI-first + Classical refine (Default).

        Steps:
        1. AI segmentation
        2. White preservation
        3. Classical refine (GrabCut)
        4. Edge feather
        5. QC check → fallback to Hybrid if needed
        """
        notes = []
        model_name = self.config['model']['ai_model']

        # Step 1: AI segmentation with alpha matting options
        alpha_matting_cfg = self.config['model'].get('alpha_matting', {})
        ai_mask = segment_with_ai(
            image,
            model_name=model_name,
            timeout_ms=self.config['performance']['timeout_ai_ms'],
            alpha_matting=alpha_matting_cfg.get('enabled', False),
            alpha_matting_foreground_threshold=alpha_matting_cfg.get('foreground_threshold', 240),
            alpha_matting_background_threshold=alpha_matting_cfg.get('background_threshold', 10),
            alpha_matting_erode_size=alpha_matting_cfg.get('erode_size', 10),
            post_process_mask=self.config['model'].get('post_process_mask', False)
        )

        if ai_mask is None:
            raise RuntimeError("AI segmentation failed")

        # Step 2: White preservation
        if self.config['refinement']['white_preservation']['enabled']:
            ai_mask = apply_white_preservation(
                image, ai_mask,
                hsv_s_threshold=self.config['refinement']['white_preservation']['hsv_s_threshold'],
                hsv_v_threshold=self.config['refinement']['white_preservation']['hsv_v_threshold'],
                lab_l_threshold=self.config['refinement']['white_preservation']['lab_l_threshold']
            )

        # Step 3: Check QC for fallback decision
        metrics = calculate_qc_metrics(image, ai_mask)
        qc_result = check_qc_thresholds(metrics, self.config['qc'])

        # If QC fails fallback thresholds → auto Hybrid
        if not qc_result['pass_fallback']:
            notes.append("QC fallback triggered → Hybrid refine")

            # Run classical
            classical_mask = segment_with_classical(
                image,
                timeout_ms=self.config['performance']['timeout_classical_ms']
            )

            if classical_mask is not None:
                # Merge with hybrid strategy
                alpha_mask = select_best_merge_strategy(ai_mask, classical_mask, image)
                notes.append("Hybrid merge applied")
            else:
                # Classical failed, use AI only
                alpha_mask = ai_mask
                notes.append("Classical fallback failed, using AI only")
        else:
            # QC passed, apply refinement
            if self.config['refinement']['grabcut_enabled']:
                alpha_mask = refine_ai_mask_with_grabcut(
                    image, ai_mask,
                    iterations=self.config['refinement']['grabcut_iterations']
                )
                notes.append("GrabCut refinement applied")
            else:
                alpha_mask = ai_mask

        # Step 4: Edge feather
        feather_px = self.config['refinement']['edge_feather_px']
        if feather_px > 0:
            alpha_mask = apply_edge_feather(alpha_mask, feather_px=feather_px)

        # Add QC warnings
        if not qc_result['pass_basic']:
            notes.extend(qc_result['warnings'])

        return {
            'alpha_mask': alpha_mask,
            'model': model_name,
            'notes': notes
        }

    def _process_mode_b(self, image: np.ndarray, input_path: str) -> Dict[str, Any]:
        """
        Mode B: Classical-first + AI fallback.

        Steps:
        1. Classical segmentation
        2. QC check → fallback to AI if failed
        3. Edge feather
        """
        notes = []

        # Step 1: Classical segmentation
        classical_mask = segment_with_classical(
            image,
            timeout_ms=self.config['performance']['timeout_classical_ms']
        )

        if classical_mask is None:
            notes.append("Classical failed → AI fallback")
            # Fallback to AI
            return self._process_mode_a(image, input_path)

        # Step 2: QC check
        metrics = calculate_qc_metrics(image, classical_mask)
        qc_result = check_qc_thresholds(metrics, self.config['qc'])

        if not qc_result['pass_basic']:
            notes.append("Classical QC failed → AI fallback")
            # Fallback to AI
            return self._process_mode_a(image, input_path)

        # QC passed, use classical result
        alpha_mask = classical_mask

        # Step 3: Edge feather
        feather_px = self.config['refinement']['edge_feather_px']
        if feather_px > 0:
            alpha_mask = apply_edge_feather(alpha_mask, feather_px=feather_px)

        return {
            'alpha_mask': alpha_mask,
            'model': 'Classical',
            'notes': notes
        }

    def _process_mode_c(self, image: np.ndarray, input_path: str) -> Dict[str, Any]:
        """
        Mode C: Hybrid-merge.

        Steps:
        1. Run AI and Classical in parallel (or sequentially)
        2. Merge masks using hybrid strategy
        3. Apply white preservation
        4. Edge feather
        """
        notes = []
        model_name = self.config['model']['ai_model']

        # Step 1: Run AI with alpha matting options
        alpha_matting_cfg = self.config['model'].get('alpha_matting', {})
        ai_mask = segment_with_ai(
            image,
            model_name=model_name,
            timeout_ms=self.config['performance']['timeout_ai_ms'],
            alpha_matting=alpha_matting_cfg.get('enabled', False),
            alpha_matting_foreground_threshold=alpha_matting_cfg.get('foreground_threshold', 240),
            alpha_matting_background_threshold=alpha_matting_cfg.get('background_threshold', 10),
            alpha_matting_erode_size=alpha_matting_cfg.get('erode_size', 10),
            post_process_mask=self.config['model'].get('post_process_mask', False)
        )

        # Step 2: Run Classical
        classical_mask = segment_with_classical(
            image,
            timeout_ms=self.config['performance']['timeout_classical_ms']
        )

        # Step 3: Merge
        if ai_mask is not None and classical_mask is not None:
            alpha_mask = select_best_merge_strategy(ai_mask, classical_mask, image)
            notes.append("Hybrid merge (AI + Classical)")
        elif ai_mask is not None:
            alpha_mask = ai_mask
            notes.append("Classical failed, using AI only")
        elif classical_mask is not None:
            alpha_mask = classical_mask
            notes.append("AI failed, using Classical only")
        else:
            raise RuntimeError("Both AI and Classical segmentation failed")

        # Step 4: White preservation
        if self.config['refinement']['white_preservation']['enabled']:
            alpha_mask = apply_white_preservation(
                image, alpha_mask,
                hsv_s_threshold=self.config['refinement']['white_preservation']['hsv_s_threshold'],
                hsv_v_threshold=self.config['refinement']['white_preservation']['hsv_v_threshold'],
                lab_l_threshold=self.config['refinement']['white_preservation']['lab_l_threshold']
            )

        # Step 5: Edge feather
        feather_px = self.config['refinement']['edge_feather_px']
        if feather_px > 0:
            alpha_mask = apply_edge_feather(alpha_mask, feather_px=feather_px)

        return {
            'alpha_mask': alpha_mask,
            'model': f"{model_name} + Classical",
            'notes': notes
        }

    def save_debug_masks(self, input_path: str, original: np.ndarray,
                        ai_mask: Optional[np.ndarray],
                        final_alpha: np.ndarray,
                        output_folder: str):
        """
        Save debug masks (side-by-side preview).

        Args:
            input_path: Input image path
            original: Original image (BGR)
            ai_mask: AI mask (if available)
            final_alpha: Final alpha mask
            output_folder: Output folder
        """
        # This will be implemented if debug_masks_enabled is True
        # For now, placeholder
        pass
