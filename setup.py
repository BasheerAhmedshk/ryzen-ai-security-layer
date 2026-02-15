# setup.py
"""
Setup configuration for AMD Ryzen AI Security Layer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amd-security-layer",
    version="1.0.0",
    author="OnePiece Team",
    author_email="team@example.com",
    description="Lightweight On-Device AI Security Layer using AMD Ryzen AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/amd-security-layer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "onnxruntime>=1.14.0",
        "onnx>=1.13.0",
    ],
    extras_require={
        "gpu": ["torch>=2.0.0"],
        "ml": ["transformers>=4.30.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "flake8>=6.0.0"],
    },
    entry_points={
        "console_scripts": [
            "amd-security=src.security_core.threat_engine:main",
        ],
    },
)
