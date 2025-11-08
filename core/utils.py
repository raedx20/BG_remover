"""
Utility functions for image processing and file handling.
"""
import os
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image


def get_orientation_suffix(width: int, height: int) -> str:
    """
    Determine orientation suffix based on final size.

    Args:
        width: Image width
        height: Image height

    Returns:
        Orientation suffix: _PRT, _LSC, or _SQR_LSC
    """
    ratio = max(width, height) / max(min(width, height), 1)

    if height > width * 1.05:
        return "_PRT"
    elif width > height * 1.05:
        return "_LSC"
    else:
        # Near-square (±5%)
        return "_SQR_LSC"


def scan_images(folder: str, extensions: List[str], recursive: bool = True) -> List[str]:
    """
    Scan folder for image files.

    Args:
        folder: Source folder path
        extensions: List of file extensions (without dot)
        recursive: Whether to scan recursively

    Returns:
        List of image file paths
    """
    image_files = []
    extensions_lower = [ext.lower() for ext in extensions]

    if recursive:
        for root, dirs, files in os.walk(folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower().lstrip('.')
                if ext in extensions_lower:
                    image_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                ext = os.path.splitext(file)[1].lower().lstrip('.')
                if ext in extensions_lower:
                    image_files.append(path)

    return sorted(image_files)


def get_output_path(input_path: str, output_folder: str, overwrite_policy: str,
                    width: int, height: int) -> str:
    """
    Generate output path with orientation suffix.

    Args:
        input_path: Input file path
        output_folder: Output folder
        overwrite_policy: 'skip', 'overwrite', or 'disambiguate'
        width: Final image width
        height: Final image height

    Returns:
        Output file path (PNG)
    """
    basename = os.path.basename(input_path)
    name, _ = os.path.splitext(basename)
    suffix = get_orientation_suffix(width, height)

    output_name = f"{name}{suffix}.png"
    output_path = os.path.join(output_folder, output_name)

    if overwrite_policy == "disambiguate" and os.path.exists(output_path):
        counter = 1
        while True:
            output_name = f"{name}{suffix}_{counter}.png"
            output_path = os.path.join(output_folder, output_name)
            if not os.path.exists(output_path):
                break
            counter += 1

    return output_path


def resize_for_processing(image: np.ndarray, max_side: int) -> Tuple[np.ndarray, float]:
    """
    Resize image for processing while maintaining aspect ratio.

    Args:
        image: Input image (BGR or BGRA)
        max_side: Maximum side length

    Returns:
        Tuple of (resized_image, scale_factor)
    """
    h, w = image.shape[:2]
    max_dim = max(h, w)

    if max_dim <= max_side:
        return image.copy(), 1.0

    scale = max_side / max_dim
    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, scale


def upscale_mask(mask: np.ndarray, target_shape: Tuple[int, int]) -> np.ndarray:
    """
    Upscale mask to target shape.

    Args:
        mask: Binary mask (0-255)
        target_shape: Target (height, width)

    Returns:
        Upscaled mask
    """
    return cv2.resize(mask, (target_shape[1], target_shape[0]),
                     interpolation=cv2.INTER_LINEAR)


def load_image_rgb(path: str) -> np.ndarray:
    """
    Load image as RGB numpy array.

    Args:
        path: Image file path

    Returns:
        RGB image array
    """
    img = Image.open(path).convert('RGB')
    return np.array(img)


def load_image_bgr(path: str) -> np.ndarray:
    """
    Load image as BGR numpy array (OpenCV format).

    Args:
        path: Image file path

    Returns:
        BGR image array
    """
    return cv2.imread(path, cv2.IMREAD_COLOR)


def save_rgba(image: np.ndarray, alpha: np.ndarray, path: str):
    """
    Save image with alpha channel as PNG.

    Args:
        image: RGB or BGR image
        alpha: Alpha channel (0-255)
        path: Output path
    """
    if image.shape[2] == 3:
        # Ensure RGB order for PIL
        if cv2.__version__:  # Assume BGR from OpenCV
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
    else:
        image_rgb = image

    # Create RGBA
    rgba = np.dstack((image_rgb, alpha))

    # Save with PIL
    img_pil = Image.fromarray(rgba.astype(np.uint8), mode='RGBA')
    img_pil.save(path, 'PNG')


def trim_transparent_borders(image: np.ndarray, alpha: np.ndarray,
                             margin: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Trim transparent borders with safe margin.

    Args:
        image: RGB/BGR image
        alpha: Alpha channel
        margin: Safe margin in pixels

    Returns:
        Tuple of (trimmed_image, trimmed_alpha)
    """
    # Find bounding box of non-transparent pixels
    coords = cv2.findNonZero(alpha)

    if coords is None:
        # Fully transparent, return minimal image
        return image[:1, :1], alpha[:1, :1]

    x, y, w, h = cv2.boundingRect(coords)

    # Apply safe margin
    h_max, w_max = alpha.shape
    x1 = max(0, x - margin)
    y1 = max(0, y - margin)
    x2 = min(w_max, x + w + margin)
    y2 = min(h_max, y + h + margin)

    trimmed_image = image[y1:y2, x1:x2]
    trimmed_alpha = alpha[y1:y2, x1:x2]

    return trimmed_image, trimmed_alpha
