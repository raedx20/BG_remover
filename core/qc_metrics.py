"""
Quality control metrics for segmentation evaluation.
"""
import cv2
import numpy as np
from typing import Dict, Any


def calculate_qc_metrics(image: np.ndarray, alpha_mask: np.ndarray) -> Dict[str, Any]:
    """
    Calculate quality control metrics for segmentation.

    Args:
        image: RGB or BGR image
        alpha_mask: Alpha channel (0-255)

    Returns:
        Dictionary containing QC metrics:
        - fg_ratio: Foreground ratio (percentage)
        - edge_confidence: Edge confidence (Laplacian median)
        - border_whiteness: Border whiteness score (informative only)
    """
    h, w = alpha_mask.shape

    # 1. Foreground ratio
    fg_pixels = np.sum(alpha_mask > 128)
    total_pixels = h * w
    fg_ratio = (fg_pixels / total_pixels) * 100.0

    # 2. Edge confidence (Laplacian median)
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Calculate Laplacian
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_abs = np.abs(laplacian)

    # Get edges from alpha mask
    edges = cv2.Canny(alpha_mask, 100, 200)
    edge_pixels = edges > 0

    if np.sum(edge_pixels) > 0:
        edge_confidence = np.median(laplacian_abs[edge_pixels])
    else:
        edge_confidence = 0.0

    # 3. Border whiteness (informative only)
    # Sample border pixels (outer 5% of image)
    border_thickness = max(1, int(min(h, w) * 0.05))

    # Create border mask
    border_mask = np.zeros((h, w), dtype=np.uint8)
    border_mask[:border_thickness, :] = 255  # Top
    border_mask[-border_thickness:, :] = 255  # Bottom
    border_mask[:, :border_thickness] = 255  # Left
    border_mask[:, -border_thickness:] = 255  # Right

    border_pixels = border_mask > 0

    if len(image.shape) == 3:
        # Calculate average brightness in border
        border_bgr = image[border_pixels]
        border_brightness = np.mean(border_bgr)
    else:
        border_brightness = np.mean(gray[border_pixels])

    # Normalize to 0-100
    border_whiteness = (border_brightness / 255.0) * 100.0

    return {
        'fg_ratio': fg_ratio,
        'edge_confidence': edge_confidence,
        'border_whiteness': border_whiteness
    }


def check_qc_thresholds(metrics: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check QC metrics against thresholds.

    Args:
        metrics: QC metrics from calculate_qc_metrics()
        config: Configuration dict with QC thresholds

    Returns:
        Dictionary with:
        - pass_basic: Basic QC passed (within normal bounds)
        - pass_fallback: Fallback QC passed (within strict bounds for Mode A)
        - warnings: List of warning messages
    """
    warnings = []

    fg_ratio = metrics['fg_ratio']
    edge_conf = metrics['edge_confidence']

    # Basic QC thresholds (for warning/info)
    fg_min = config.get('fg_ratio_min', 10)
    fg_max = config.get('fg_ratio_max', 90)
    edge_min = config.get('edge_confidence_min', 14)

    # Fallback QC thresholds (for Mode A fallback to hybrid)
    fallback_fg_min = config.get('fallback_fg_ratio_min', 8)
    fallback_fg_max = config.get('fallback_fg_ratio_max', 95)
    fallback_edge_min = config.get('fallback_edge_confidence_min', 12)

    # Check basic QC
    pass_basic = True
    if fg_ratio < fg_min:
        warnings.append(f"Low foreground ratio: {fg_ratio:.1f}% (expected >= {fg_min}%)")
        pass_basic = False
    elif fg_ratio > fg_max:
        warnings.append(f"High foreground ratio: {fg_ratio:.1f}% (expected <= {fg_max}%)")
        pass_basic = False

    if edge_conf < edge_min:
        warnings.append(f"Low edge confidence: {edge_conf:.1f} (expected >= {edge_min})")
        pass_basic = False

    # Check fallback QC (stricter for Mode A auto-hybrid trigger)
    pass_fallback = True
    if fg_ratio < fallback_fg_min or fg_ratio > fallback_fg_max:
        pass_fallback = False
    if edge_conf < fallback_edge_min:
        pass_fallback = False

    return {
        'pass_basic': pass_basic,
        'pass_fallback': pass_fallback,
        'warnings': warnings
    }
