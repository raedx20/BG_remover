"""
Setup script for Background Remover CLI
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bg-remover-white",
    version="1.0.0",
    author="BG Remover Team",
    description="Enhanced background remover for white-on-white product images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raedx20/BG_remover",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python>=4.8.0",
        "opencv-contrib-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "rembg[cli]>=2.0.50",
        "click>=8.1.0",
        "tqdm>=4.65.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "gui": ["PyQt5>=5.15.9"],
        "gpu": ["onnxruntime-gpu>=1.15.0"],
    },
    entry_points={
        "console_scripts": [
            "bg-remover=bg_remover_cli:cli",
        ],
    },
)
