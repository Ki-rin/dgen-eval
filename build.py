#!/usr/bin/env python3
"""
Build script for Documentation Evaluation Dashboard

This script performs the following tasks:
1. Organizes the project into a proper package structure
2. Builds the Python package
3. Creates distribution packages (wheel, sdist)
4. Optionally builds the Docker image

Usage:
    python build.py [--docker] [--publish] [--no-package]
"""

import os
import sys
import shutil
import argparse
import subprocess
import platform
from pathlib import Path
import re

# Configuration
PROJECT_NAME = "doc_evaluator"
PACKAGE_FILES = [
    # Core files
    "app.py", "dashboard.py", "healthcheck.py", "init_eval_environment.py", "start.py",
    "cli.py",
    
    # Directories to copy
    "core", "evaluators", "llm", "pipeline",
    
    # Config and examples are copied separately
]

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build Documentation Evaluation Dashboard")
    parser.add_argument("--docker", action="store_true", help="Build Docker image")
    parser.add_argument("--publish", action="store_true", help="Publish package to PyPI")
    parser.add_argument("--no-package", action="store_true", help="Skip Python package building")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts before building")
    parser.add_argument("--version", type=str, help="Override version number")
    return parser.parse_args()

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()

def clean_build_artifacts():
    """Clean up build artifacts."""
    dirs_to_clean = ["build", "dist", f"{PROJECT_NAME}.egg-info"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            shutil.rmtree(dir_name)

def setup_package_structure():
    """Set up the package directory structure."""
    # Create package directory if it doesn't exist
    os.makedirs(PROJECT_NAME, exist_ok=True)
    
    # Copy files to package directory
    for file_or_dir in PACKAGE_FILES:
        src_path = Path(file_or_dir)
        dst_path = Path(PROJECT_NAME) / src_path.name
        
        if src_path.is_file():
            print(f"Copying file: {src_path} -> {dst_path}")
            shutil.copy2(src_path, dst_path)
        elif src_path.is_dir():
            if dst_path.exists():
                shutil.rmtree(dst_path)
            print(f"Copying directory: {src_path} -> {dst_path}")
            shutil.copytree(src_path, dst_path)
    
    # Create subdirectories for config and examples
    os.makedirs(f"{PROJECT_NAME}/config", exist_ok=True)
    os.makedirs(f"{PROJECT_NAME}/examples", exist_ok=True)
    
    # Copy config and example files
    for yaml_file in Path("config").glob("*.yaml"):
        dst_path = Path(f"{PROJECT_NAME}/config") / yaml_file.name
        print(f"Copying config: {yaml_file} -> {dst_path}")
        shutil.copy2(yaml_file, dst_path)
    
    for md_file in Path("examples").glob("*.md"):
        dst_path = Path(f"{PROJECT_NAME}/examples") / md_file.name
        print(f"Copying example: {md_file} -> {dst_path}")
        shutil.copy2(md_file, dst_path)

def update_version(version=None):
    """Update the version in __init__.py."""
    if not version:
        return
    
    init_file = Path(f"{PROJECT_NAME}/__init__.py")
    if init_file.exists():
        content = init_file.read_text()
        new_content = re.sub(
            r'__version__ = "[^"]+"',
            f'__version__ = "{version}"',
            content
        )
        init_file.write_text(new_content)
        print(f"Updated version to {version} in {init_file}")

def build_python_package():
    """Build the Python package."""
    print("\n=== Building Python package ===")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel", "build", "twine"])
    run_command([sys.executable, "-m", "build"])

def build_docker_image():
    """Build the Docker image."""
    print("\n=== Building Docker image ===")
    
    # Determine Docker or Podman
    docker_cmd = "docker"
    if shutil.which("podman") and not shutil.which("docker"):
        docker_cmd = "podman"
    
    # Build the image
    image_name = f"doc-evaluator-dashboard:latest"
    run_command([docker_cmd, "build", "-t", image_name, "."])
    print(f"Docker image built successfully: {image_name}")

def publish_to_pypi():
    """Publish the package to PyPI."""
    print("\n=== Publishing to PyPI ===")
    
    # Check if .pypirc exists
    pypirc_path = os.path.expanduser("~/.pypirc")
    if not os.path.exists(pypirc_path):
        print("Warning: ~/.pypirc not found. You may need to authenticate with PyPI.")
    
    # Upload to PyPI
    run_command([sys.executable, "-m", "twine", "upload", "dist/*"])
    print("Package published to PyPI successfully!")

def main():
    """Main function."""
    args = parse_args()
    
    print("=== Documentation Evaluation Dashboard Build Tool ===")
    
    # Clean artifacts if requested
    if args.clean:
        clean_build_artifacts()
    
    # Set up package structure
    print("\n=== Setting up package structure ===")
    setup_package_structure()
    
    # Update version if provided
    if args.version:
        update_version(args.version)
    
    # Build Python package
    if not args.no_package:
        build_python_package()
    
    # Build Docker image if requested
    if args.docker:
        build_docker_image()
    
    # Publish to PyPI if requested
    if args.publish and not args.no_package:
        publish_to_pypi()
    
    print("\n=== Build completed successfully! ===")

if __name__ == "__main__":
    main()