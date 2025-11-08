#!/usr/bin/env python3
"""
Diagnostic script to test Background Remover setup.
This will help identify what's causing the AI segmentation failures.
"""
import sys

def test_python_version():
    """Check Python version."""
    print("=" * 60)
    print("1. TESTING PYTHON VERSION")
    print("=" * 60)
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8+ required!")
        return False
    print("✅ Python version OK")
    return True


def test_opencv():
    """Test OpenCV import."""
    print("\n" + "=" * 60)
    print("2. TESTING OPENCV")
    print("=" * 60)
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"❌ ERROR: OpenCV not installed - {e}")
        return False


def test_numpy():
    """Test NumPy import."""
    print("\n" + "=" * 60)
    print("3. TESTING NUMPY")
    print("=" * 60)
    try:
        import numpy as np
        print(f"✅ NumPy version: {np.__version__}")
        return True
    except ImportError as e:
        print(f"❌ ERROR: NumPy not installed - {e}")
        return False


def test_pillow():
    """Test Pillow import."""
    print("\n" + "=" * 60)
    print("4. TESTING PILLOW")
    print("=" * 60)
    try:
        from PIL import Image
        import PIL
        print(f"✅ Pillow version: {PIL.__version__}")
        return True
    except ImportError as e:
        print(f"❌ ERROR: Pillow not installed - {e}")
        return False


def test_rembg():
    """Test rembg import."""
    print("\n" + "=" * 60)
    print("5. TESTING REMBG")
    print("=" * 60)
    try:
        import rembg
        print(f"✅ rembg installed")

        # Check if we can import key functions
        from rembg import remove, new_session
        print("✅ rembg functions available")
        return True
    except ImportError as e:
        print(f"❌ ERROR: rembg not installed - {e}")
        print("\nTo fix: Run 'pip install rembg' or 'install.bat'")
        return False


def test_onnxruntime():
    """Test onnxruntime import."""
    print("\n" + "=" * 60)
    print("6. TESTING ONNXRUNTIME (AI Engine)")
    print("=" * 60)
    try:
        import onnxruntime as ort
        print(f"✅ onnxruntime version: {ort.__version__}")

        # Check available providers
        providers = ort.get_available_providers()
        print(f"✅ Available providers: {', '.join(providers)}")

        if 'CPUExecutionProvider' in providers:
            print("✅ CPU execution available")

        return True
    except ImportError as e:
        print(f"❌ ERROR: onnxruntime not installed - {e}")
        print("\nonnxruntime is required by rembg for AI processing")
        print("To fix: Run 'pip install onnxruntime' or 'install.bat'")
        return False


def test_pyqt5():
    """Test PyQt5 import."""
    print("\n" + "=" * 60)
    print("7. TESTING PYQT5 (GUI)")
    print("=" * 60)
    try:
        from PyQt5 import QtCore
        print(f"✅ PyQt5 version: {QtCore.QT_VERSION_STR}")
        return True
    except ImportError as e:
        print(f"❌ ERROR: PyQt5 not installed - {e}")
        return False


def test_simple_segmentation():
    """Test actual AI segmentation on a simple test image."""
    print("\n" + "=" * 60)
    print("8. TESTING AI SEGMENTATION (ACTUAL)")
    print("=" * 60)

    try:
        import numpy as np
        from PIL import Image
        from rembg import remove, new_session

        # Create a simple test image (100x100 red square)
        print("Creating test image...")
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        test_img[25:75, 25:75] = [255, 0, 0]  # Red square
        pil_img = Image.fromarray(test_img)

        print("Initializing AI model (this may take a minute)...")
        print("  - Downloading model if first time (~176 MB)")
        print("  - Please wait...")

        # Try to create session
        session = new_session('isnet-general-use')
        print("✅ Model session created successfully")

        # Try to remove background
        print("Testing background removal...")
        output = remove(pil_img, session=session)
        print("✅ Background removal successful!")

        # Check output
        output_np = np.array(output)
        if output_np.shape[2] == 4:
            print(f"✅ Output has alpha channel (shape: {output_np.shape})")

        return True

    except Exception as e:
        print(f"❌ ERROR during AI segmentation test:")
        print(f"   {type(e).__name__}: {e}")

        # Additional diagnostics
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()

        return False


def test_yaml():
    """Test YAML import."""
    print("\n" + "=" * 60)
    print("9. TESTING YAML")
    print("=" * 60)
    try:
        import yaml
        print(f"✅ PyYAML installed")
        return True
    except ImportError as e:
        print(f"❌ ERROR: PyYAML not installed - {e}")
        return False


def main():
    """Run all diagnostic tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "BACKGROUND REMOVER - SETUP DIAGNOSTIC" + " " * 10 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        test_python_version,
        test_numpy,
        test_pillow,
        test_opencv,
        test_pyqt5,
        test_yaml,
        test_onnxruntime,  # Critical for AI
        test_rembg,        # Critical for AI
        test_simple_segmentation  # Actual test
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR in {test.__name__}: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        print("\nYour setup is complete and working correctly.")
        print("If you're still getting errors, please check:")
        print("  1. Image file paths (avoid special characters)")
        print("  2. Available disk space (models need ~500MB)")
        print("  3. Internet connection (for first-time model download)")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nTo fix issues:")
        print("  1. Run 'install.bat' again")
        print("  2. Or manually run: pip install -r requirements.txt")
        print("  3. Make sure you have internet connection")
        print("  4. Check you have ~500MB free disk space")

    print("\n" + "=" * 60)
    input("\nPress Enter to close...")


if __name__ == '__main__':
    main()
