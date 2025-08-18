"""
Setup script for Flip-Flop Prompter.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flip-flop-prompter",
    version="0.1.0",
    author="Flip-Flop Prompter Team",
    author_email="contact@flipflopprompter.com",
    description="AI Model Prompt Formulation Tool for text-to-image and text-to-video models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flip-flop-prompter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "gui": [
            "tkinter",  # Usually comes with Python
        ],
    },
    entry_points={
        "console_scripts": [
            "flip-flop-prompter=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    keywords="ai, prompt, generation, text-to-image, text-to-video, seedream, veo, flux, wan, hailuo",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/flip-flop-prompter/issues",
        "Source": "https://github.com/yourusername/flip-flop-prompter",
        "Documentation": "https://github.com/yourusername/flip-flop-prompter/docs",
    },
)
