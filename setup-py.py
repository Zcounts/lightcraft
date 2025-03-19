#!/usr/bin/env python3
"""
Setup script for LightCraft.
"""

from setuptools import setup, find_packages

setup(
    name="lightcraft",
    version="0.1.0",
    description="Lighting Diagram Designer for Film Shoots",
    author="LightCraft Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.5.0",
        "Pillow>=9.5.0",
        "reportlab>=3.6.12",
    ],
    entry_points={
        "console_scripts": [
            "lightcraft=lightcraft.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
