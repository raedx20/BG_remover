# Quick Start Guide for Beginners 🚀

**A simple, step-by-step guide to remove backgrounds from your product images!**

No technical knowledge required. Works on **any Windows PC** with Intel Iris Xe or any CPU - **no dedicated GPU needed!**

---

## What You Need

✅ **Windows 10 or 11** (Mac/Linux users see README.md)
✅ **Internet connection** (for downloading libraries and AI models)
✅ **10-15 minutes** for setup (only once!)
✅ **Your product images** (JPG, PNG, WebP)

**You DO NOT need:**
- ❌ Graphics card (GPU)
- ❌ Programming knowledge
- ❌ Command line experience

---

## Step 1: Install Python (One-Time Setup)

**If you already have Python 3.8+, skip to Step 2!**

1. Go to: https://www.python.org/downloads/
2. Click the big yellow button: **"Download Python 3.x.x"**
3. Run the installer
4. ⚠️ **IMPORTANT**: Check the box **"Add Python to PATH"**
5. Click **"Install Now"**
6. Wait for installation to complete
7. Click **"Close"**

**How to check if Python is installed:**
- Press `Windows + R`
- Type: `cmd`
- Press Enter
- Type: `python --version`
- You should see something like: `Python 3.11.x`

---

## Step 2: Download This Application

**Option A: Download ZIP (Easiest)**
1. Click the green **"Code"** button on GitHub
2. Click **"Download ZIP"**
3. Extract the ZIP file to a folder (e.g., `C:\BG_Remover`)
4. Remember this location!

**Option B: Git Clone (Advanced)**
```bash
git clone <repository-url>
cd BG_remover
```

---

## Step 3: Install Required Libraries (One-Time Setup)

1. **Open the folder** where you extracted the files
2. **Double-click**: `install.bat`
3. **Wait** 5-10 minutes (it will download all needed libraries)
4. When you see **"SUCCESS! Installation Complete!"**, you're done!

**What install.bat does:**
- ✅ Checks if Python is installed
- ✅ Downloads OpenCV, NumPy, Pillow
- ✅ Downloads rembg (AI background removal)
- ✅ Downloads PyQt5 (GUI)
- ✅ Tests that everything works

**Common Issues:**

**"Python is not installed"**
→ Go back to Step 1 and install Python

**"Access Denied" or "Permission Error"**
→ Right-click `install.bat` → Run as Administrator

**"pip is not recognized"**
→ Reinstall Python and check "Add Python to PATH"

---

## Step 4: Run the Application

**Method 1: Double-Click (Easiest)**
1. Double-click: `run.bat`
2. Wait for the GUI window to open

**Method 2: Command Line**
1. Open Command Prompt in the BG_Remover folder
2. Type: `python app.py`
3. Press Enter

**First Run Note:**
- The app will download AI models (100-200MB)
- This takes 1-5 minutes depending on your internet
- ☕ Grab a coffee! This only happens once.
- Models are saved to: `C:\Users\YourName\.u2net\`

---

## Step 5: Remove Backgrounds! 🎉

### For Quick Results (Recommended for Beginners)

**Tab 1: Input**
1. Click **"Browse..."**
2. Select the folder with your product images
3. Click **"Scan for Images"**
4. You should see a list of found images

**Tab 2: Output & Naming**
1. Click **"Browse..."**
2. Choose where to save processed images
3. ⚠️ Must be a **different** folder from input!

**Tab 4: CPG Presets** ⭐ (New! Super Easy!)
1. Check **"Enable CPG Preset"**
2. Select your product type:
   - 🍾 Transparent/Glass → Bottles, jars
   - ✨ Glossy → Cosmetics, shampoo
   - 📦 Food Packaging → Cereal, snacks
   - 🥤 Beverage → Soda cans, drinks
   - 🥛 White Products → Milk, detergent
   - 💄 Beauty → Makeup, skincare
   - 🧹 Household → Cleaning supplies
   - 🥫 Metallic → Aluminum cans

**Tab 8: Run**
1. Click **"Start Processing"**
2. Watch the progress bar!
3. When done, click **"Open Output Folder"**

**That's it!** Your images now have transparent backgrounds! 🎉

---

## Step 6: Understanding the Results

**Output Files:**
- All images saved as **PNG** with transparency
- Named with orientation suffix:
  - `product_PRT.png` = Portrait (tall)
  - `product_LSC.png` = Landscape (wide)
  - `product_SQR_LSC.png` = Square

**CSV Report:**
- Saved in output folder
- Shows success/failure for each image
- Includes processing time and quality metrics

---

## Advanced Tips (Optional)

### Manual Settings (Skip if using CPG Presets)

**If you don't use CPG Presets, configure these tabs:**

**Tab 3: Processing Mode**
- **Mode A** (Default): Best for most products
- **Mode B**: Faster for simple backgrounds
- **Mode C**: Best quality for tricky products

**Tab 5: Model & Refinement**
- **AI Model**: Use `isnet-general` (default) for products
- **Alpha Matting**: Enable for complex edges (slower but better)
- **White Preservation**: Prevents white details from disappearing

**Tab 6: QC & Logging**
- **Debug Masks**: Turn on to see diagnostic previews

**Tab 7: Performance**
- **Concurrency**: Set to "Auto" (uses your CPU cores)
- **Max Side**: 1800px works well for most images

---

## Troubleshooting for Beginners

### "Application won't start"

**Check 1:** Is Python installed?
```
python --version
```
Should show Python 3.8 or higher

**Check 2:** Did you run install.bat?
- Look for "SUCCESS!" message
- If not, run it again

**Check 3:** Are you in the right folder?
- You should see `app.py` in the folder
- Make sure you extracted the ZIP file

### "No images found"

- Check that images are JPG, PNG, or WebP
- Make sure "Scan subfolders recursively" is checked
- Try clicking "Scan for Images" again

### "Output folder must be different from input"

- Input and output folders **cannot** be the same
- Create a new folder like `C:\BG_Remover_Output`

### "Processing is very slow"

- **Normal!** AI processing takes time
- First image: 10-30 seconds
- Subsequent images: 5-15 seconds each
- Use **Mode B** for faster processing (Tab 3)
- Enable **Concurrency** to process multiple images at once (Tab 7)

### "White parts of my product disappeared"

- Use **CPG Preset**: 🥛 White Products (Tab 4)
- Or manually: Increase white preservation (Tab 5)
- Lower `HSV S threshold` to 20
- Increase `Lab L threshold` to 90

### "Edges look rough or have halos"

- Enable **Alpha Matting** (Tab 5)
- Increase **Edge Feather** to 4-5 pixels (Tab 5)
- Try **Mode C** (Hybrid) for best quality (Tab 3)

---

## System Requirements

**Minimum:**
- Windows 10 or 11
- Intel Iris Xe (or any CPU from last 10 years)
- 4 GB RAM
- 2 GB free disk space

**Recommended:**
- Windows 11
- Intel Core i5 or better
- 8 GB RAM
- SSD for faster processing

**Works Great On:**
- ✅ Intel Iris Xe (your GPU!)
- ✅ Intel HD Graphics
- ✅ AMD Ryzen with integrated graphics
- ✅ Any modern CPU (no dedicated GPU needed!)

---

## How Long Does Processing Take?

**On Intel Iris Xe / Modern CPU:**

| Number of Images | Time (Estimate) |
|-----------------|-----------------|
| 1 image | 10-30 seconds |
| 10 images | 2-5 minutes |
| 50 images | 10-25 minutes |
| 100 images | 20-50 minutes |

**Tips to speed up:**
- Use **Mode B** (Classical-first) - Tab 3
- Increase **Concurrency** (Auto or 4 threads) - Tab 7
- Use **u2netp** model (lightweight, faster) - Tab 5
- Process images in batches

---

## What Files Can I Delete Later?

**Keep:**
- `app.py`, `config.yaml` - Main application
- `core/`, `gui/` folders - Program code
- `requirements.txt` - Needed for updates

**Can Delete:**
- `install.bat`, `run.bat` - Only needed for setup/launch
- `README.md`, `QUICK_START.md` - Documentation
- CSV reports in output folder - After reviewing
- `__pycache__` folders - Auto-generated

**DO NOT Delete:**
- `C:\Users\YourName\.u2net\` - Contains downloaded AI models (large!)
  - If you delete this, models will re-download on next run

---

## Next Steps

**Learn More:**
- Read `README.md` for advanced features
- Experiment with different CPG Presets
- Try Manual settings for fine control

**Join the Community:**
- Report issues on GitHub
- Share your results
- Request new features

**Optimize Your Workflow:**
- Create custom config files for different product types
- Use batch processing for large catalogs
- Explore all 8 CPG preset categories

---

## FAQ for Absolute Beginners

**Q: Do I need to know programming?**
A: No! Just double-click `run.bat` and use the GUI.

**Q: Will this work on my laptop?**
A: Yes! Works on any Windows PC from the last 10 years.

**Q: Do I need a graphics card (GPU)?**
A: No! Works perfectly on CPU only (Intel Iris Xe included).

**Q: How much does this cost?**
A: 100% free and open-source!

**Q: Can I process 1000 images?**
A: Yes! Batch processing supports unlimited images.

**Q: Will it damage my computer?**
A: No! It's just like running any other program.

**Q: How do I update to the latest version?**
A: Download new ZIP, extract, run `install.bat` again.

**Q: Can I use this for commercial work?**
A: Check the license file for usage terms.

---

## Still Need Help?

**Option 1: Check the Error Message**
- Read what it says carefully
- Google the exact error message
- Check Troubleshooting section above

**Option 2: GitHub Issues**
- Go to the GitHub repository
- Click "Issues"
- Search for similar problems
- Create new issue if needed

**Option 3: Documentation**
- `README.md` - Complete documentation
- `config.yaml` - All settings explained

---

## Summary: The Absolute Easiest Way

**For complete beginners who just want it to work:**

1. **Install Python** (check "Add to PATH")
2. **Download and extract ZIP**
3. **Double-click** `install.bat`
4. **Double-click** `run.bat`
5. **Tab 1**: Select input folder, click Scan
6. **Tab 2**: Select output folder
7. **Tab 4**: Enable CPG Preset, pick product type
8. **Tab 8**: Click "Start Processing"
9. **Done!** Check output folder

**That's literally it!** No command line, no coding, just click buttons! 🎉

---

## Success! What Now?

**You've successfully removed backgrounds!**

✅ **Check your results** - Open output folder
✅ **Review CSV report** - See success rate
✅ **Experiment** - Try different presets
✅ **Process more** - Run another batch
✅ **Share feedback** - Help improve the tool

**Welcome to easy background removal!** 🚀
