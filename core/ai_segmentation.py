"""
AI-based segmentation using rembg with enhanced features.
Enhanced version with full rembg model support and alpha matting.
"""
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Dict, Any
import io


# Lazy import rembg to avoid slow startup
_rembg_session = {}


# All available rembg models
AVAILABLE_MODELS = {
    'u2net': {
        'name': 'u2net',
        'description': 'General purpose, good accuracy',
        'size': '~176 MB',
        'best_for': 'General images'
    },
    'u2netp': {
        'name': 'u2netp',
        'description': 'Lightweight, faster',
        'size': '~4.7 MB',
        'best_for': 'Speed-critical applications'
    },
    'u2net_human_seg': {
        'name': 'u2net_human_seg',
        'description': 'Optimized for human segmentation',
        'size': '~176 MB',
        'best_for': 'People/portraits'
    },
    'u2net_cloth_seg': {
        'name': 'u2net_cloth_seg',
        'description': 'Clothing/fashion segmentation',
        'size': '~176 MB',
        'best_for': 'Clothing products'
    },
    'silueta': {
        'name': 'silueta',
        'description': 'High-quality silhouettes',
        'size': '~43 MB',
        'best_for': 'Clean silhouettes'
    },
    'isnet-general-use': {
        'name': 'isnet-general-use',
        'description': 'Best for products (Default)',
        'size': '~176 MB',
        'best_for': 'Product images'
    },
    'isnet-anime': {
        'name': 'isnet-anime',
        'description': 'Optimized for anime/illustrations',
        'size': '~176 MB',
        'best_for': 'Anime/cartoon images'
    },
    'sam': {
        'name': 'sam',
        'description': 'Segment Anything Model',
        'size': '~358 MB',
        'best_for': 'Complex scenes'
    }
}


def get_rembg_session(model_name: str):
    """
    Get or create rembg session for specified model.

    Args:
        model_name: Model identifier (see AVAILABLE_MODELS)

    Returns:
        Rembg session
    """
    global _rembg_session

    if model_name not in _rembg_session:
        try:
            from rembg import new_session

            # Map friendly names to rembg model names
            model_map = {
                'isnet-general': 'isnet-general-use',
                'u2net': 'u2net',
                'u2netp': 'u2netp',
                'u2net-human': 'u2net_human_seg',
                'u2net-cloth': 'u2net_cloth_seg',
                'silueta': 'silueta',
                'isnet-anime': 'isnet-anime',
                'sam': 'sam'
            }

            rembg_model = model_map.get(model_name, model_name)

            # Validate model exists
            if rembg_model not in AVAILABLE_MODELS:
                print(f"Warning: Unknown model '{model_name}', using 'isnet-general-use'")
                rembg_model = 'isnet-general-use'

            _rembg_session[model_name] = new_session(rembg_model)

        except Exception as e:
            raise RuntimeError(f"Failed to initialize rembg model '{model_name}': {e}")

    return _rembg_session[model_name]


def segment_with_ai(image: np.ndarray, model_name: str = 'isnet-general',
                    timeout_ms: int = 12000,
                    alpha_matting: bool = False,
                    alpha_matting_foreground_threshold: int = 240,
                    alpha_matting_background_threshold: int = 10,
                    alpha_matting_erode_size: int = 10,
                    post_process_mask: bool = False) -> Optional[np.ndarray]:
    """
    Perform AI-based segmentation using rembg with enhanced options.

    Args:
        image: RGB or BGR image
        model_name: Model to use (see AVAILABLE_MODELS)
        timeout_ms: Timeout in milliseconds (currently not enforced)
        alpha_matting: Enable alpha matting for better edges
        alpha_matting_foreground_threshold: Foreground threshold (0-255)
        alpha_matting_background_threshold: Background threshold (0-255)
        alpha_matting_erode_size: Erosion size for matting
        post_process_mask: Apply morphological post-processing

    Returns:
        Alpha mask (0-255) or None if failed
    """
    try:
        from rembg import remove

        # Convert to RGB PIL Image
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume BGR from OpenCV
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        pil_image = Image.fromarray(image_rgb.astype(np.uint8))

        # Get session
        session = get_rembg_session(model_name)

        # Remove background with enhanced options
        output = remove(
            pil_image,
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_size=alpha_matting_erode_size,
            post_process_mask=post_process_mask,
            only_mask=False  # Return RGBA
        )

        # Extract alpha channel
        output_np = np.array(output)

        if output_np.shape[2] == 4:
            alpha_mask = output_np[:, :, 3]
        else:
            # Fallback: create mask from non-black pixels
            gray = cv2.cvtColor(output_np[:, :, :3], cv2.COLOR_RGB2GRAY)
            alpha_mask = (gray > 10).astype(np.uint8) * 255

        return alpha_mask

    except Exception as e:
        print(f"AI segmentation failed: {e}")
        return None


def get_model_info(model_name: str = None) -> Dict[str, Any]:
    """
    Get information about available models.

    Args:
        model_name: Specific model name, or None for all models

    Returns:
        Dictionary with model information
    """
    if model_name:
        # Map friendly names
        model_map = {
            'isnet-general': 'isnet-general-use',
            'u2net-human': 'u2net_human_seg',
            'u2net-cloth': 'u2net_cloth_seg'
        }
        actual_name = model_map.get(model_name, model_name)
        return AVAILABLE_MODELS.get(actual_name, {})
    else:
        return AVAILABLE_MODELS


def refine_ai_mask_with_grabcut(image: np.ndarray, ai_mask: np.ndarray,
                                 iterations: int = 4) -> np.ndarray:
    """
    Refine AI mask using GrabCut seeded from AI segmentation.

    Args:
        image: BGR image
        ai_mask: AI-generated alpha mask (0-255)
        iterations: Number of GrabCut iterations (3-5 recommended)

    Returns:
        Refined alpha mask (0-255)
    """
    try:
        # Create GrabCut mask from AI mask
        # GC_BGD = 0, GC_FGD = 1, GC_PR_BGD = 2, GC_PR_FGD = 3

        gc_mask = np.zeros(ai_mask.shape, dtype=np.uint8)

        # Definite background: AI mask = 0
        gc_mask[ai_mask < 50] = 0  # GC_BGD

        # Definite foreground: AI mask core (eroded)
        from core.white_preservation import erode_mask_core
        ai_core = erode_mask_core(ai_mask, iterations=2)
        gc_mask[ai_core > 200] = 1  # GC_FGD

        # Probable foreground: AI mask edge region
        gc_mask[(ai_mask >= 50) & (ai_core <= 200)] = 3  # GC_PR_FGD

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
        return ai_mask  # Return original on failure


def create_definite_masks(ai_mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create definite foreground and background masks from AI mask.

    Args:
        ai_mask: AI-generated alpha mask (0-255)

    Returns:
        Tuple of (definite_fg, definite_bg) binary masks
    """
    from core.white_preservation import erode_mask_core, dilate_mask_border

    # Definite foreground: eroded core
    definite_fg = erode_mask_core(ai_mask, iterations=3)
    definite_fg = (definite_fg > 200).astype(np.uint8) * 255

    # Definite background: inverted and dilated
    inverted = 255 - ai_mask
    definite_bg = dilate_mask_border(inverted, iterations=3)
    definite_bg = (definite_bg > 200).astype(np.uint8) * 255

    return definite_fg, definite_bg
