# Background Remover - White Product Edition

A comprehensive background removal tool specifically optimized for white and near-white product images. Built on **[rembg](https://github.com/danielgatis/rembg)** with enhanced features including white preservation, classical segmentation, alpha matting, and intelligent quality control.

## Features

### Core Capabilities
- **Enhanced rembg Integration**: Direct integration with all 8 rembg models
  - `isnet-general` - Best for products (Default, 176MB)
  - `u2net` - General purpose (176MB)
  - `u2netp` - Lightweight/faster (4.7MB)
  - `u2net-human` - People/portraits (176MB)
  - `u2net-cloth` - Clothing/fashion (176MB)
  - `silueta` - High-quality silhouettes (43MB)
  - `isnet-anime` - Anime/illustrations (176MB)
  - `sam` - Segment Anything Model (358MB)

- **Advanced rembg Features**:
  - **Alpha Matting**: Better edge quality for complex/hairy edges
  - **Post-processing**: Built-in morphological mask operations
  - Optimized session management with model caching

- **Our Enhancements**:
  - **White Preservation Algorithm**: Prevents white product details from being removed
  - **Classical Segmentation**: Lab color distance + GrabCut refinement
  - **Three Processing Modes**: AI-first, Classical-first, or Hybrid merge
  - **Batch Processing**: Multi-threaded with progress tracking
  - **Quality Control**: Automated QC metrics with intelligent fallback
  - **CSV Reporting**: Detailed per-image metrics
  - **Smart Naming**: Automatic orientation detection (_PRT, _LSC, _SQR_LSC)
  - **Full GUI**: PyQt5 interface with all settings configurable

### White Preservation Algorithm

The white preservation algorithm is the key differentiator for white-on-white products:

- Analyzes pixels using both HSV and Lab color spaces
- Identifies low-saturation, high-luminance pixels (likely white product details)
- Preserves these pixels inside the detected product boundary
- Prevents loss of white labels, caps, highlights, and reflective surfaces
- Configurable thresholds for fine-tuning

**Default Settings:**
- HSV: S ≤ 25, V ≥ 220
- Lab: L ≥ 85

## Installation

### Requirements
- Python 3.8 or higher
- PyQt5 for GUI
- OpenCV for image processing
- rembg for AI segmentation

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd BG_remover

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### First-Time Setup

On first run, rembg will automatically download the AI models (100-200MB). This happens once and is cached locally.

## Usage

### GUI Application

Launch the application:
```bash
python app.py
```

#### Tab-by-Tab Guide

**1. Input Tab**
- Select source folder containing images
- Configure file extensions (jpg, jpeg, png, webp)
- Enable/disable recursive subfolder scanning
- Click "Scan" to preview detected files

**2. Output & Naming Tab**
- Select output folder (must differ from input)
- Choose overwrite policy:
  - **Skip**: Leave existing files unchanged
  - **Overwrite**: Replace existing files
  - **Disambiguate** (default): Add number suffix (_1, _2, etc.)
- Naming rules are automatic based on orientation:
  - `_PRT`: Portrait (height > width × 1.05)
  - `_LSC`: Landscape (width > height × 1.05)
  - `_SQR_LSC`: Square/Near-square (±5%)

**3. Processing Mode Tab**
- **Mode A** (Default): Best for most products
  - AI segmentation → White preservation → GrabCut refinement
  - Auto-switches to Hybrid if AI produces poor results
- **Mode B**: Faster for simple backgrounds
  - Classical segmentation first
  - Falls back to AI if QC fails
- **Mode C**: Maximum quality for challenging images
  - Runs both AI and Classical in parallel
  - Intelligently merges results
- **Force AI** checkbox: Override mode for troubleshooting

**4. CPG Presets Tab** ⭐ NEW!
- **Optimized for Consumer Packaged Goods**:
  - 🍾 **Transparent/Glass**: Bottles, jars, clear containers with transparency
  - ✨ **Glossy/Reflective**: Cosmetics, shampoo, lotions, glossy packaging
  - 📦 **Food Packaging**: Cereal boxes, snack bags, frozen food
  - 🥤 **Beverage**: Soda cans, bottles (opaque and transparent)
  - 🥛 **White Products**: Milk, bleach, white detergent, dairy
  - 💄 **Beauty/Cosmetics**: Makeup, skincare, beauty products
  - 🧹 **Household**: Cleaning supplies, detergents
  - 🥫 **Metallic/Cans**: Aluminum cans, aerosol, foil

- **How CPG Presets Work**:
  - One-click optimization for your product type
  - Automatically configures AI model, alpha matting, processing mode
  - Overrides manual settings when enabled
  - Fine-tuned for CPG product characteristics (reflections, transparency, text preservation)

**5. Model & Refinement Tab**
- **AI Model** (Choose from 8 rembg models):
  - `isnet-general` - Best for products (Default, 176MB)
  - `u2net` - General purpose (176MB)
  - `u2netp` - Lightweight/faster (4.7MB)
  - `u2net-human` - People/portraits (176MB)
  - `u2net-cloth` - Clothing/fashion (176MB)
  - `silueta` - High-quality silhouettes (43MB)
  - `isnet-anime` - Anime/illustrations (176MB)
  - `sam` - Segment Anything Model (358MB)

- **Alpha Matting** (rembg native feature):
  - Enable for complex/hairy edges (slower but better quality)
  - Foreground threshold: 0-255 (default: 240)
  - Background threshold: 0-255 (default: 10)
  - Erode size: 1-30 (default: 10)
  - Post-processing: Apply rembg's morphological operations

- **Refinement** (Our enhancements):
  - Edge feather: 0-10 pixels (default: 3)
  - GrabCut refinement: ON by default, 3-5 iterations

- **White Preservation** (Our key feature - Always enabled):
  - Configure HSV and Lab thresholds
  - Lower S threshold = more aggressive preservation
  - Higher V/L threshold = only brightest whites

- **Trimming**: Remove transparent borders with safe margin

**6. QC & Logging Tab**
- **QC Metrics** (for warnings):
  - Expected foreground ratio: 10-90%
  - Edge confidence minimum: 14
- **Fallback Thresholds** (Mode A only):
  - Stricter thresholds that trigger auto-Hybrid
  - FG ratio: 8-95%
  - Edge confidence: 12
- **Debug Masks**: Enable to save diagnostic previews (OFF by default)

**7. Performance Tab**
- **Concurrency**: Auto (CPU-based) or Fixed thread count
- **Max Side**: Downscale limit for processing (1600-2000px recommended)
- **Timeouts**: AI (12s) and Classical (4s) per image
- **Queue Order**: Natural (alphabetical) or Smallest-first

**8. Run Tab**
- Click "Start Processing" to begin
- Monitor progress bar and live log
- Log format: `# | filename | Mode | Model | FG% | Edge | time ms | ✓/✖`
- Open output folder or CSV report when complete

### Configuration Files

Settings are automatically saved to `config.yaml`. You can:
- Save/load custom configurations via File menu
- Edit YAML directly for scripting
- Share configurations across machines

Example `config.yaml`:
```yaml
input:
  source_folder: "/path/to/images"
  extensions: [jpg, jpeg, png, webp]
  recursive: true

processing:
  mode: "A"
  force_ai_all: false

model:
  ai_model: "isnet-general"

refinement:
  edge_feather_px: 3
  grabcut_enabled: true
  white_preservation:
    hsv_s_threshold: 25
    hsv_v_threshold: 220
```

## Processing Modes Explained

### Mode A: AI-first + Classical Refine (Default)

**Best for:** Most product images, especially white-on-white

**Process:**
1. AI segmentation using selected model
2. White preservation applied to prevent detail loss
3. GrabCut refinement seeded from AI mask
4. Edge feathering for smooth transitions
5. QC check → auto-switches to Hybrid if needed

**Fallback Logic:**
- If AI FG ratio < 8% or > 95%: Switch to Hybrid
- If edge confidence < 12: Switch to Hybrid
- Hybrid = merge AI + Classical masks

### Mode B: Classical-first + AI Fallback

**Best for:** Simple white backgrounds, faster processing

**Process:**
1. Estimate background color from borders
2. Lab color distance mask
3. GrabCut refinement
4. QC check → AI fallback if needed
5. Edge feathering

**Fallback Logic:**
- If FG ratio out of bounds: Use Mode A instead
- If edge confidence too low: Use Mode A instead

### Mode C: Hybrid-merge

**Best for:** Complex/challenging images, maximum quality

**Process:**
1. Run AI segmentation
2. Run Classical segmentation (parallel or sequential)
3. Intelligently merge masks based on edge confidence
4. White preservation applied to merged result
5. Edge feathering

**Merge Strategy:**
- High agreement (IoU > 70%): Simple weighted blend
- Medium agreement (40-70%): Edge-aware hybrid
- Low agreement (< 40%): Trust AI more (global understanding)

## Quality Control Metrics

### Foreground Ratio
- Percentage of non-transparent pixels
- Typical range: 10-90%
- Too low (< 8%): Product barely visible, possible failure
- Too high (> 95%): Possible background not removed

### Edge Confidence
- Laplacian median of edges
- Measures edge sharpness/clarity
- Typical range: 14+
- Low values (< 12): Soft/blurry edges, may need refinement

### Border Whiteness
- Informative only, not used for rejection
- Indicates background brightness
- High values (> 90): White background confirmed

## CSV Report Format

Generated CSV includes:

| Column | Description |
|--------|-------------|
| input_path | Source image path |
| output_path | Output PNG path |
| mode | Processing mode (A/B/C) |
| model | AI model used or "Classical" |
| fg_ratio | Foreground percentage (0-100) |
| edge_conf | Edge confidence score |
| elapsed_ms | Processing time in milliseconds |
| status | success / failed |
| notes | Warnings, fallbacks, errors |

## CPG Product Optimization ⭐ NEW!

### What are CPG Presets?

CPG (Consumer Packaged Goods) presets are one-click optimized settings for different types of packaged products. Each preset automatically configures:
- Best AI model for the product type
- Optimal alpha matting settings
- Processing mode (A/B/C)
- White preservation thresholds
- Refinement parameters

### When to Use CPG Presets

**Use CPG Presets when:**
- Processing e-commerce product photography
- Working with specific product categories (cosmetics, beverages, food packaging)
- You want optimal settings without manual tuning
- Processing batches of similar products

**Use Manual Settings when:**
- You need fine-grained control
- Working with unique/non-standard products
- Experimenting with different approaches

### CPG Preset Guide

#### 🍾 Transparent/Glass Products
**Best for:** Water bottles, perfume bottles, skincare jars, glass containers
**Key Features:**
- Alpha matting enabled for transparent edges
- Mode C (Hybrid) for best transparency handling
- Higher background threshold to preserve transparency
- Optimized for see-through materials

#### ✨ Glossy/Reflective Products
**Best for:** Cosmetics, shampoo bottles, conditioner, lotions
**Key Features:**
- Preserves highlights and reflections
- Lower saturation threshold for glossy highlights
- Mode A (AI-first) handles reflections well
- No post-processing to keep metallic finishes

#### 📦 Food Packaging
**Best for:** Cereal boxes, snack bags, frozen food boxes, candy packages
**Key Features:**
- Standard settings optimized for printed text
- Post-processing for clean edges
- Good text preservation
- Mode A for reliable results

#### 🥤 Beverage Containers
**Best for:** Soda cans, beer bottles, juice bottles, energy drinks
**Key Features:**
- Handles both opaque cans and transparent bottles
- Alpha matting for bottle transparency
- Mode C (Hybrid) for mixed materials
- Sharp edges for metallic cans

#### 🥛 White Products
**Best for:** Milk cartons, bleach bottles, white detergent, dairy products
**Key Features:**
- **Most aggressive white preservation**
- Very high Lab L threshold (90)
- Extra edge feathering for white blending
- Prevents white-on-white detail loss

#### 💄 Beauty & Cosmetics
**Best for:** Lipstick, foundation, eyeshadow, skincare, compacts
**Key Features:**
- Premium quality settings
- Sharp edges for clean product shots
- Preserves metallic and glossy finishes
- Mode A for best quality

#### 🧹 Household Products
**Best for:** Cleaning supplies, detergents, dish soap, paper products
**Key Features:**
- Standard CPG settings
- Reliable for most household items
- Good text preservation
- Mode A (AI-first)

#### 🥫 Metallic/Cans
**Best for:** Aluminum cans, aerosol cans, metal containers, foil packaging
**Key Features:**
- Optimized for metallic reflections
- Alpha matting for reflective edges
- Mode C (Hybrid) for complex reflections
- Preserves bright metallic highlights

### How to Use CPG Presets

1. **Open Tab 4: CPG Presets**
2. **Check "Enable CPG Preset"**
3. **Select your product type** from the dropdown
4. **Read the description** to confirm it matches your products
5. **Process your images** - preset automatically applies

**Note:** When CPG preset is enabled, it overrides manual settings from the Model & Refinement tab.

### CPG Preset Examples

**Scenario 1: E-commerce cosmetics shoot**
- Product: Luxury skincare bottles (glossy)
- Preset: ✨ Glossy/Reflective
- Result: Perfect preservation of glossy highlights and reflections

**Scenario 2: Beverage product catalog**
- Product: Mixed soda cans and bottles
- Preset: 🥤 Beverage
- Result: Clean metallic cans, transparent bottles with content visible

**Scenario 3: White dairy products**
- Product: Milk cartons, yogurt containers
- Preset: 🥛 White Products
- Result: Zero white detail loss, perfect text preservation

## Tuning Guide

### Common Scenarios

#### White Labels Disappearing
**Problem:** White text or labels on white products are becoming transparent

**Solution:**
1. Lower `hsv_s_threshold` (try 20 or 15)
2. Lower `hsv_v_threshold` (try 200)
3. Use Mode A or Mode C (not Mode B)
4. Enable debug masks to visualize

#### Halos Around Edges
**Problem:** Visible white/gray border around product

**Solution:**
1. Increase `edge_feather_px` to 4-5
2. Enable GrabCut refinement (should be ON)
3. Increase GrabCut iterations to 5
4. Try Mode C for better edge detection

#### Background Not Fully Removed
**Problem:** White background pixels remain around product

**Solution:**
1. Try Mode A with Force AI enabled
2. Switch to u2net model (more aggressive)
3. Increase `trimming.safe_margin_px` to 4-5
4. Check that background is actually white (> 90% in QC)

#### Dark Products on White Background
**Problem:** Dark/colorful products easier than white products

**Solution:**
- Use Mode B (faster, classical works well)
- Or Mode A (reliable, auto-fallback)
- Reduce `edge_feather_px` to 2 for sharper edges
- Increase edge confidence thresholds

#### Low-Contrast Edges
**Problem:** Product edges very similar to background

**Solution:**
1. Use Mode C (Hybrid) for maximum effort
2. Enable GrabCut with 5 iterations
3. Lower fallback thresholds to trigger Hybrid more often
4. Try different AI models (u2net vs isnet-general)

### Performance Optimization

#### Faster Processing
- Use Mode B (Classical-first)
- Select u2netp model (lightweight)
- Increase concurrency (more threads)
- Increase max_side_px limit (less downscaling)
- Process smallest files first

#### Higher Quality
- Use Mode C (Hybrid)
- Select isnet-general model
- Reduce concurrency (1-2 threads for consistency)
- Decrease max_side_px (more detail preservation)
- Enable debug masks to verify results

## Troubleshooting

### Installation Issues

**rembg fails to install:**
```bash
# Try installing with no-cache-dir
pip install --no-cache-dir rembg

# Or install dependencies separately
pip install onnxruntime
pip install rembg
```

**OpenCV import errors:**
```bash
# Uninstall conflicting packages
pip uninstall opencv-python opencv-contrib-python

# Reinstall
pip install opencv-python opencv-contrib-python
```

**PyQt5 not found:**
```bash
# Install PyQt5
pip install PyQt5

# On Linux, may need system packages
sudo apt-get install python3-pyqt5
```

### Runtime Issues

**Application won't start:**
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip list`
- Run from terminal to see error messages: `python app.py`

**Models not downloading:**
- Check internet connection
- Models are downloaded to `~/.u2net/` on first use
- May require 100-200MB download
- Check disk space

**Processing fails on all images:**
- Verify input folder contains valid images
- Check file permissions (read input, write output)
- Ensure output folder ≠ input folder
- Check log for specific error messages

**Out of memory errors:**
- Reduce max_side_px (try 1200-1400)
- Reduce concurrency (try 1-2 threads)
- Process smaller batches
- Close other applications

### Debug Workflow

1. **Enable debug masks** in QC & Logging tab
2. **Process one image** first to test
3. **Check CSV report** for metrics
4. **Review debug previews** to see AI mask vs final
5. **Adjust settings** based on observations
6. **Re-test** with same image
7. **Scale up** to full batch once satisfied

## Success Criteria (Phase 1)

As specified in requirements:

- ✅ **0 images with "white eaten" defects** on golden set
- ✅ **≤ 5% with visible halo** (edge feathering fixes)
- ✅ **≥ 90% pass in Mode A** without manual tweaks

## Architecture

```
BG_remover/
├── app.py                      # Main entry point
├── config.yaml                 # Configuration file
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── core/                       # Core processing modules
│   ├── processor.py            # Main processor (Modes A/B/C)
│   ├── ai_segmentation.py      # AI models (rembg)
│   ├── classical_segmentation.py  # Lab distance, GrabCut
│   ├── hybrid.py               # Mask merging strategies
│   ├── white_preservation.py   # White preservation algorithm
│   ├── qc_metrics.py           # Quality control
│   ├── batch_processor.py      # Batch processing, CSV
│   └── utils.py                # Utilities
└── gui/                        # GUI components
    ├── main_window.py          # Main window
    └── tabs/                   # Tab widgets
        ├── input_tab.py
        ├── output_tab.py
        ├── mode_tab.py
        ├── model_tab.py
        ├── qc_tab.py
        ├── performance_tab.py
        └── run_tab.py
```

## Future Enhancements (Phase 2+)

- GPU acceleration (PyTorch CUDA) for AI
- In-GUI previews (before/after)
- Fine-tuning isnet-general on custom white-product dataset
- Batch preview mode (review before processing)
- Undo/redo for individual images
- Custom mask editing
- Shadow preservation option
- Reflection preservation
- Multi-output formats (TIFF, WebP)

## License

[Specify license]

## Credits

- **rembg**: Background removal models (https://github.com/danielgatis/rembg)
- **OpenCV**: Image processing library
- **PyQt5**: GUI framework

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Check troubleshooting section above
- Review CSV report and debug masks for diagnostics

---

**Version:** 1.0
**Last Updated:** 2025-01-08
