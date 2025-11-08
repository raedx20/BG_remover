"""
Hybrid segmentation mode combining AI and Classical methods.
"""
import cv2
import numpy as np
from typing import Tuple


def merge_masks_hybrid(ai_mask: np.ndarray, classical_mask: np.ndarray,
                       image: np.ndarray) -> np.ndarray:
    """
    Merge AI and Classical masks using edge confidence.

    Strategy:
    - AI mask defines global foreground/background
    - Classical mask refines edges where it has higher confidence
    - Use Laplacian/gradient to determine edge confidence

    Args:
        ai_mask: Alpha mask from AI (0-255)
        classical_mask: Alpha mask from Classical (0-255)
        image: Original BGR image

    Returns:
        Merged alpha mask (0-255)
    """
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate edge confidence using Laplacian
    laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=3)
    edge_strength = np.abs(laplacian)

    # Normalize edge strength to 0-1
    edge_strength_norm = edge_strength / (np.max(edge_strength) + 1e-6)

    # Detect edge regions from both masks
    ai_edges = cv2.Canny(ai_mask, 50, 150)
    classical_edges = cv2.Canny(classical_mask, 50, 150)

    # Combine edge regions
    all_edges = cv2.bitwise_or(ai_edges, classical_edges)

    # Dilate to create edge zone
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    edge_zone = cv2.dilate(all_edges, kernel, iterations=1)

    # Create merged mask
    merged_mask = ai_mask.copy().astype(np.float32)

    # In edge zone: blend based on edge confidence
    # High edge confidence → trust classical more
    # Low edge confidence → trust AI more
    edge_pixels = edge_zone > 0

    if np.sum(edge_pixels) > 0:
        # Blend weight: higher edge strength → more classical
        classical_weight = edge_strength_norm[edge_pixels] * 0.7  # Max 70% classical
        ai_weight = 1.0 - classical_weight

        merged_mask[edge_pixels] = (
            ai_mask[edge_pixels].astype(np.float32) * ai_weight +
            classical_mask[edge_pixels].astype(np.float32) * classical_weight
        )

    # Outside edge zone: use AI mask (more global understanding)
    # Already copied above

    # Convert back to uint8
    merged_mask = np.clip(merged_mask, 0, 255).astype(np.uint8)

    return merged_mask


def merge_masks_simple(ai_mask: np.ndarray, classical_mask: np.ndarray,
                       ai_weight: float = 0.7) -> np.ndarray:
    """
    Simple weighted merge of AI and Classical masks.

    Args:
        ai_mask: Alpha mask from AI (0-255)
        classical_mask: Alpha mask from Classical (0-255)
        ai_weight: Weight for AI mask (0-1), default 0.7

    Returns:
        Merged alpha mask (0-255)
    """
    merged = (
        ai_mask.astype(np.float32) * ai_weight +
        classical_mask.astype(np.float32) * (1.0 - ai_weight)
    )

    return np.clip(merged, 0, 255).astype(np.uint8)


def merge_masks_max(ai_mask: np.ndarray, classical_mask: np.ndarray) -> np.ndarray:
    """
    Merge masks using maximum (union of foregrounds).

    Args:
        ai_mask: Alpha mask from AI (0-255)
        classical_mask: Alpha mask from Classical (0-255)

    Returns:
        Merged alpha mask (0-255)
    """
    return np.maximum(ai_mask, classical_mask)


def merge_masks_min(ai_mask: np.ndarray, classical_mask: np.ndarray) -> np.ndarray:
    """
    Merge masks using minimum (intersection of foregrounds).

    Args:
        ai_mask: Alpha mask from AI (0-255)
        classical_mask: Alpha mask from Classical (0-255)

    Returns:
        Merged alpha mask (0-255)
    """
    return np.minimum(ai_mask, classical_mask)


def select_best_merge_strategy(ai_mask: np.ndarray, classical_mask: np.ndarray,
                                image: np.ndarray) -> np.ndarray:
    """
    Automatically select best merge strategy based on mask agreement.

    Args:
        ai_mask: Alpha mask from AI (0-255)
        classical_mask: Alpha mask from Classical (0-255)
        image: Original BGR image

    Returns:
        Merged alpha mask (0-255)
    """
    # Calculate mask agreement (IoU)
    ai_binary = (ai_mask > 128).astype(np.uint8)
    classical_binary = (classical_mask > 128).astype(np.uint8)

    intersection = np.sum(ai_binary & classical_binary)
    union = np.sum(ai_binary | classical_binary)

    iou = intersection / (union + 1e-6)

    # High agreement (IoU > 0.7): use simple weighted merge
    if iou > 0.7:
        return merge_masks_simple(ai_mask, classical_mask, ai_weight=0.7)

    # Medium agreement (0.4 < IoU <= 0.7): use edge-based hybrid
    elif iou > 0.4:
        return merge_masks_hybrid(ai_mask, classical_mask, image)

    # Low agreement (IoU <= 0.4): trust AI more (more global understanding)
    else:
        return merge_masks_simple(ai_mask, classical_mask, ai_weight=0.85)
