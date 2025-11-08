"""
White preservation algorithm for white-on-white products.

This module ensures that low-saturation, high-luminance pixels inside the AI mask
are preserved (not made transparent), critical for white labels, caps, and highlights
on white products.
"""
import cv2
import numpy as np


def apply_white_preservation(image: np.ndarray, alpha_mask: np.ndarray,
                             hsv_s_threshold: int = 25,
                             hsv_v_threshold: int = 220,
                             lab_l_threshold: int = 85,
                             alpha_clamp_min: int = 220) -> np.ndarray:
    """
    Apply white preservation to alpha mask.

    For pixels with low saturation and high luminance (inside AI boundary),
    clamp alpha to ensure they remain visible.

    Args:
        image: RGB or BGR image
        alpha_mask: Alpha channel (0-255), from AI segmentation
        hsv_s_threshold: HSV saturation threshold (S <= this value)
        hsv_v_threshold: HSV value threshold (V >= this value)
        lab_l_threshold: Lab lightness threshold (L >= this value)
        alpha_clamp_min: Minimum alpha value for preserved whites

    Returns:
        Modified alpha mask with white preservation applied
    """
    # Convert to RGB if BGR
    if image.shape[2] == 3:
        # Assume BGR from OpenCV
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image

    # Convert to HSV and Lab
    image_hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
    image_lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)

    # Extract channels
    h, s, v = cv2.split(image_hsv)
    l, a, b = cv2.split(image_lab)

    # Create white preservation mask
    # Method 1: HSV-based (low saturation, high value)
    white_mask_hsv = (s <= hsv_s_threshold) & (v >= hsv_v_threshold)

    # Method 2: Lab-based (high lightness)
    white_mask_lab = (l >= lab_l_threshold)

    # Combine both methods (OR)
    white_mask = white_mask_hsv | white_mask_lab

    # Only apply inside AI mask boundary (where alpha > 0)
    # This prevents preserving background whites
    inside_ai_mask = alpha_mask > 0

    # Final white preservation mask
    preserve_mask = white_mask & inside_ai_mask

    # Apply preservation: clamp alpha for preserved whites
    alpha_preserved = alpha_mask.copy()
    alpha_preserved[preserve_mask] = np.maximum(
        alpha_preserved[preserve_mask],
        alpha_clamp_min
    )

    return alpha_preserved


def apply_edge_feather(alpha_mask: np.ndarray, feather_px: int = 3) -> np.ndarray:
    """
    Apply edge feathering to alpha mask for smoother transitions.

    Args:
        alpha_mask: Alpha channel (0-255)
        feather_px: Feather radius in pixels

    Returns:
        Feathered alpha mask
    """
    if feather_px <= 0:
        return alpha_mask

    # Create a binary mask
    binary = (alpha_mask > 128).astype(np.uint8) * 255

    # Find edges
    edges = cv2.Canny(binary, 100, 200)

    # Dilate edges to create feather zone
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                       (feather_px * 2 + 1, feather_px * 2 + 1))
    feather_zone = cv2.dilate(edges, kernel, iterations=1)

    # Apply Gaussian blur in feather zone
    blurred = cv2.GaussianBlur(alpha_mask, (feather_px * 2 + 1, feather_px * 2 + 1), 0)

    # Blend original and blurred based on feather zone
    alpha_feathered = alpha_mask.copy()
    mask_3ch = feather_zone > 0
    alpha_feathered[mask_3ch] = blurred[mask_3ch]

    return alpha_feathered


def erode_mask_core(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    """
    Erode mask to create a definite foreground core.

    Args:
        mask: Binary mask (0-255)
        iterations: Number of erosion iterations

    Returns:
        Eroded mask
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    return cv2.erode(mask, kernel, iterations=iterations)


def dilate_mask_border(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    """
    Dilate mask to create a definite background border.

    Args:
        mask: Binary mask (0-255)
        iterations: Number of dilation iterations

    Returns:
        Dilated mask
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    return cv2.dilate(mask, kernel, iterations=iterations)
