"""
CPG (Consumer Packaged Goods) Presets
Optimized settings for different types of CPG products.
"""
from typing import Dict, Any


# CPG Product Categories and Optimized Settings
CPG_PRESETS = {
    'cpg-transparent': {
        'name': 'Transparent/Glass Products',
        'description': 'Bottles, jars, clear containers with transparency',
        'examples': 'Water bottles, perfume, skincare jars, glass containers',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': True,  # Critical for transparent edges
                    'foreground_threshold': 230,  # Lower to capture transparent edges
                    'background_threshold': 15,   # Higher to preserve transparency
                    'erode_size': 8
                },
                'post_process_mask': True  # Clean up transparent artifacts
            },
            'refinement': {
                'edge_feather_px': 2,  # Less feather for sharp transparent edges
                'grabcut_enabled': True,
                'grabcut_iterations': 5,  # More iterations for complex edges
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 30,  # Higher for transparent whites
                    'hsv_v_threshold': 210,
                    'lab_l_threshold': 80
                }
            },
            'processing': {
                'mode': 'C'  # Hybrid for best results on transparency
            }
        }
    },

    'cpg-glossy': {
        'name': 'Glossy/Reflective Products',
        'description': 'Shiny surfaces, cosmetics, shampoo bottles',
        'examples': 'Cosmetics, shampoo, conditioner, lotions, glossy packaging',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': True,
                    'foreground_threshold': 240,
                    'background_threshold': 10,
                    'erode_size': 10
                },
                'post_process_mask': False  # Preserve glossy highlights
            },
            'refinement': {
                'edge_feather_px': 3,
                'grabcut_enabled': True,
                'grabcut_iterations': 4,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 20,  # Lower to preserve highlights
                    'hsv_v_threshold': 230,  # Higher for bright reflections
                    'lab_l_threshold': 88
                }
            },
            'processing': {
                'mode': 'A'  # AI-first handles reflections well
            }
        }
    },

    'cpg-food-packaging': {
        'name': 'Food Packaging',
        'description': 'Boxes, bags, wrappers with text and graphics',
        'examples': 'Cereal boxes, snack bags, frozen food, candy packages',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': False,  # Not needed for solid packaging
                    'foreground_threshold': 240,
                    'background_threshold': 10,
                    'erode_size': 10
                },
                'post_process_mask': True  # Clean edges
            },
            'refinement': {
                'edge_feather_px': 3,
                'grabcut_enabled': True,
                'grabcut_iterations': 4,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 25,  # Standard for text preservation
                    'hsv_v_threshold': 220,
                    'lab_l_threshold': 85
                }
            },
            'processing': {
                'mode': 'A'  # AI-first for clean results
            }
        }
    },

    'cpg-beverage': {
        'name': 'Beverage Containers',
        'description': 'Cans, bottles (opaque and transparent)',
        'examples': 'Soda cans, beer bottles, juice bottles, energy drinks',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': True,  # For bottle transparency
                    'foreground_threshold': 235,
                    'background_threshold': 12,
                    'erode_size': 9
                },
                'post_process_mask': True
            },
            'refinement': {
                'edge_feather_px': 2,  # Sharp edges for cans/bottles
                'grabcut_enabled': True,
                'grabcut_iterations': 5,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 28,
                    'hsv_v_threshold': 215,
                    'lab_l_threshold': 83
                }
            },
            'processing': {
                'mode': 'C'  # Hybrid for mixed materials
            }
        }
    },

    'cpg-white-products': {
        'name': 'White CPG Products',
        'description': 'Predominantly white packaging (milk, cleaning products)',
        'examples': 'Milk cartons, bleach, white detergent bottles, dairy products',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': True,  # For edge refinement
                    'foreground_threshold': 245,  # Higher for white preservation
                    'background_threshold': 8,
                    'erode_size': 12
                },
                'post_process_mask': False  # Preserve white details
            },
            'refinement': {
                'edge_feather_px': 4,  # More feather for white blending
                'grabcut_enabled': True,
                'grabcut_iterations': 5,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 20,  # Very aggressive white preservation
                    'hsv_v_threshold': 235,
                    'lab_l_threshold': 90  # Very high for white products
                }
            },
            'processing': {
                'mode': 'A'  # AI-first with aggressive white preservation
            }
        }
    },

    'cpg-beauty-cosmetics': {
        'name': 'Beauty & Cosmetics',
        'description': 'Makeup, skincare, beauty products',
        'examples': 'Lipstick, foundation, eyeshadow, skincare bottles, compacts',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': True,  # For fine details and reflections
                    'foreground_threshold': 240,
                    'background_threshold': 10,
                    'erode_size': 10
                },
                'post_process_mask': False  # Preserve metallic finishes
            },
            'refinement': {
                'edge_feather_px': 2,  # Sharp edges for clean product shots
                'grabcut_enabled': True,
                'grabcut_iterations': 4,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 22,
                    'hsv_v_threshold': 225,
                    'lab_l_threshold': 86
                }
            },
            'processing': {
                'mode': 'A'  # AI-first for premium quality
            }
        }
    },

    'cpg-household': {
        'name': 'Household Products',
        'description': 'Cleaning supplies, detergents, household items',
        'examples': 'Detergent bottles, spray cleaners, dish soap, paper products',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': False,  # Most household products are opaque
                    'foreground_threshold': 240,
                    'background_threshold': 10,
                    'erode_size': 10
                },
                'post_process_mask': True  # Clean up edges
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
                }
            },
            'processing': {
                'mode': 'A'  # AI-first, standard settings
            }
        }
    },

    'cpg-metallic': {
        'name': 'Metallic/Cans',
        'description': 'Metal cans, aluminum packaging, foil products',
        'examples': 'Aluminum cans, aerosol cans, metal containers',
        'recommended_model': 'isnet-general',
        'settings': {
            'model': {
                'ai_model': 'isnet-general',
                'alpha_matting': {
                    'enabled': True,  # For reflective edges
                    'foreground_threshold': 235,
                    'background_threshold': 12,
                    'erode_size': 8
                },
                'post_process_mask': False  # Preserve metallic reflections
            },
            'refinement': {
                'edge_feather_px': 2,  # Sharp metallic edges
                'grabcut_enabled': True,
                'grabcut_iterations': 5,
                'white_preservation': {
                    'enabled': True,
                    'hsv_s_threshold': 18,  # Low for metallic highlights
                    'hsv_v_threshold': 235,  # High for bright reflections
                    'lab_l_threshold': 88
                }
            },
            'processing': {
                'mode': 'C'  # Hybrid for complex reflections
            }
        }
    }
}


def get_cpg_preset(preset_name: str) -> Dict[str, Any]:
    """
    Get CPG preset configuration.

    Args:
        preset_name: Preset identifier

    Returns:
        Preset configuration dictionary
    """
    return CPG_PRESETS.get(preset_name, {})


def list_cpg_presets() -> Dict[str, Dict[str, str]]:
    """
    List all available CPG presets with descriptions.

    Returns:
        Dictionary of preset info
    """
    return {
        key: {
            'name': preset['name'],
            'description': preset['description'],
            'examples': preset['examples'],
            'recommended_model': preset['recommended_model']
        }
        for key, preset in CPG_PRESETS.items()
    }


def apply_cpg_preset(config: Dict[str, Any], preset_name: str) -> Dict[str, Any]:
    """
    Apply CPG preset to configuration.

    Args:
        config: Current configuration
        preset_name: Preset to apply

    Returns:
        Updated configuration
    """
    preset = get_cpg_preset(preset_name)

    if not preset:
        return config

    # Deep merge preset settings into config
    settings = preset.get('settings', {})

    for section, values in settings.items():
        if section not in config:
            config[section] = {}

        if isinstance(values, dict):
            for key, value in values.items():
                if isinstance(value, dict) and key in config[section]:
                    # Merge nested dicts
                    config[section][key].update(value)
                else:
                    config[section][key] = value
        else:
            config[section] = values

    return config


# Quick reference guide
CPG_QUICK_GUIDE = """
CPG Product Type Selection Guide:

🍾 Transparent/Glass:
   Use for: Water bottles, perfume, glass jars, clear containers
   Key: Alpha matting enabled for transparent edges

✨ Glossy/Reflective:
   Use for: Cosmetics, shampoo, lotions, glossy packaging
   Key: Preserves highlights and reflections

📦 Food Packaging:
   Use for: Cereal boxes, snack bags, frozen food
   Key: Standard settings, text preservation

🥤 Beverage:
   Use for: Soda cans, bottles, energy drinks
   Key: Handles both opaque and transparent

🥛 White Products:
   Use for: Milk, bleach, white detergent, dairy
   Key: Aggressive white preservation

💄 Beauty/Cosmetics:
   Use for: Makeup, skincare, beauty products
   Key: Premium quality, fine details

🧹 Household:
   Use for: Cleaning supplies, detergents
   Key: Standard CPG settings

🥫 Metallic/Cans:
   Use for: Aluminum cans, aerosol, foil
   Key: Handles metallic reflections
"""
