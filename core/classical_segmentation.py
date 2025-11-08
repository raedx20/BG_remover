"""
Classical segmentation methods (Lab distance, GrabCut).
"""
import cv2
import numpy as np
from typing import Optional, Tuple


def estimate_background_color(image: np.ndarray, border_fraction: float = 0.1) -> np.ndarray:
    """
    Estimate background color from image borders.

    Args:
        image: BGR image
        border_fraction: Fraction of image border to sample (0.05-0.15)

    Returns:
        Median BGR color of borders
    """
    h, w = image.shape[:2]
    border_thickness = max(1, int(min(h, w) * border_fraction))

    # Sample border pixels
    border_pixels = []

    # Top
    border_pixels.append(image[:border_thickness, :].reshape(-1, 3))
    # Bottom
    border_pixels.append(image[-border_thickness:, :].reshape(-1, 3))
    # Left
    border_pixels.append(image[:, :border_thickness].reshape(-1, 3))
    # Right
    border_pixels.append(image[:, -border_thickness:].reshape(-1, 3))

    # Concatenate all border pixels
    all_border = np.vstack(border_pixels)

    # Calculate median color
    median_color = np.median(all_border, axis=0)

    return median_color.astype(np.uint8)


def create_lab_distance_mask(image: np.ndarray, bg_color: np.ndarray,
                              threshold: float = 30.0) -> np.ndarray:
    """
    Create mask based on Lab color distance from background.

    Args:
        image: BGR image
        bg_color: Background color (BGR)
        threshold: Distance threshold (20-40 typical for white backgrounds)

    Returns:
        Binary mask (0-255) where foreground = 255
    """
    # Convert to Lab
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Create background color image
    bg_image = np.full_like(image, bg_color, dtype=np.uint8)
    bg_lab = cv2.cvtColor(bg_image, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Calculate Euclidean distance in Lab space
    distance = np.sqrt(np.sum((image_lab - bg_lab) ** 2, axis=2))

    # Threshold
    mask = (distance > threshold).astype(np.uint8) * 255

    # Clean up with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fill holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove noise

    return mask


def segment_with_classical(image: np.ndarray, timeout_ms: int = 4000,
                           lab_threshold: float = 30.0,
                           grabcut_iterations: int = 3) -> Optional[np.ndarray]:
    """
    Perform classical segmentation using Lab distance + GrabCut.

    Args:
        image: BGR image
        timeout_ms: Timeout in milliseconds (currently not enforced)
        lab_threshold: Lab distance threshold
        grabcut_iterations: Number of GrabCut iterations

    Returns:
        Alpha mask (0-255) or None if failed
    """
    try:
        # Step 1: Estimate background color
        bg_color = estimate_background_color(image, border_fraction=0.1)

        # Step 2: Create initial mask with Lab distance
        initial_mask = create_lab_distance_mask(image, bg_color, threshold=lab_threshold)

        # Step 3: Refine with GrabCut
        refined_mask = refine_classical_mask_with_grabcut(
            image, initial_mask, iterations=grabcut_iterations
        )

        return refined_mask

    except Exception as e:
        print(f"Classical segmentation failed: {e}")
        return None


def refine_classical_mask_with_grabcut(image: np.ndarray, initial_mask: np.ndarray,
                                       iterations: int = 3) -> np.ndarray:
    """
    Refine classical mask using GrabCut.

    Args:
        image: BGR image
        initial_mask: Binary mask (0-255) from Lab distance
        iterations: Number of GrabCut iterations

    Returns:
        Refined alpha mask (0-255)
    """
    try:
        from core.white_preservation import erode_mask_core, dilate_mask_border

        # Create GrabCut mask
        # GC_BGD = 0, GC_FGD = 1, GC_PR_BGD = 2, GC_PR_FGD = 3
        gc_mask = np.zeros(initial_mask.shape, dtype=np.uint8)

        # Definite foreground: eroded core
        fg_core = erode_mask_core(initial_mask, iterations=2)
        gc_mask[fg_core > 200] = 1  # GC_FGD

        # Definite background: dilated inverted
        bg_dilated = dilate_mask_border(255 - initial_mask, iterations=2)
        gc_mask[bg_dilated > 200] = 0  # GC_BGD

        # Probable foreground: transition region
        gc_mask[(initial_mask > 100) & (fg_core <= 200)] = 3  # GC_PR_FGD

        # Probable background: transition region
        gc_mask[(initial_mask <= 100) & (bg_dilated <= 200)] = 2  # GC_PR_BGD

        # Initialize models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # Run GrabCut
        cv2.grabCut(image, gc_mask, None, bgd_model, fgd_model,
                   iterations, cv2.GC_INIT_WITH_MASK)

        # Create output mask
        refined_mask = np.where((gc_mask == 1) | (gc_mask == 3), 255, 0).astype(np.uint8)

        return refined_mask

    except Exception as e:
        print(f"GrabCut refinement failed: {e}")
        return initial_mask  # Return original on failure


def adaptive_lab_threshold(image: np.ndarray, bg_color: np.ndarray) -> float:
    """
    Calculate adaptive Lab threshold based on image characteristics.

    Args:
        image: BGR image
        bg_color: Background color (BGR)

    Returns:
        Adaptive threshold value (15-40 typical range)
    """
    # Convert to Lab
    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    bg_lab = cv2.cvtColor(
        np.full((1, 1, 3), bg_color, dtype=np.uint8),
        cv2.COLOR_BGR2LAB
    ).astype(np.float32)[0, 0]

    # Calculate distance statistics
    distance = np.sqrt(np.sum((image_lab - bg_lab) ** 2, axis=2))

    # Use percentile-based threshold
    # For white-on-white: lower threshold (20-30)
    # For high contrast: higher threshold (30-40)
    p10 = np.percentile(distance, 10)
    p90 = np.percentile(distance, 90)

    contrast_range = p90 - p10

    if contrast_range < 30:
        # Low contrast (white-on-white): lower threshold
        threshold = max(15.0, p10 + 5)
    else:
        # Higher contrast: higher threshold
        threshold = min(40.0, p10 + 15)

    return threshold
