#!/usr/bin/env python3
"""
Installation script for Documentation Evaluation Dashboard

This script simplifies the installation process by:
1. Creating a virtual environment (optional)
2. Installing dependencies
3. Installing the package in development mode
4. Setting up initial directories and sample data

Usage:
    python install.py [--no-venv] [--force] [--dev]
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
import shutil
import venv

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Install Documentation Evaluation Dashboard")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--force", action="store_true", help="Force reinstallation even if already installed")
    parser.add_argument("--dev", action="store_true", help="Install in development mode")
    return parser.parse_args()

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()

def create_virtual_environment():
    """Create a virtual environment for the application."""
    venv_dir = ".venv"
    
    # Check if venv already exists
    if os.path.exists(venv_dir):
        print(f"Virtual environment already exists at {venv_dir}")
        return venv_dir
    
    print(f"Creating virtual environment at {venv_dir}...")
    venv.create(venv_dir, with_pip=True)
    return venv_dir

def get_venv_python(venv_dir):
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")

def install_package(python_exec, dev_mode=False):
    """Install the package and its dependencies."""
    # Install package with dependencies
    if dev_mode:
        print("Installing in development mode...")
        run_command([python_exec, "-m", "pip", "install", "-e", "."])
    else:
        print("Installing package...")
        run_command([python_exec, "-m", "pip", "install", "."])

def setup_directories(python_exec):
    """Set up necessary directories and initialize sample data."""
    dirs = ["config", "examples", "evaluation_results"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Generate sample data
    print("Generating sample evaluation data...")
    run_command([python_exec, "init_eval_environment.py"])

def main():
    """Main function."""
    args = parse_args()
    
    print("=== Documentation Evaluation Dashboard Installer ===")
    
    # Create virtual environment unless --no-venv is specified
    venv_dir = None
    python_exec = sys.executable
    
    if not args.no_venv:
        venv_dir = create_virtual_environment()
        python_exec = get_venv_python(venv_dir)
    
    # Install package
    install_package(python_exec, args.dev)
    
    # Set up directories and sample data
    setup_directories(python_exec)
    
    # Print success message
    print("\n=== Installation completed successfully! ===")
    if venv_dir:
        if platform.system() == "Windows":
            activate_cmd = f"{venv_dir}\\Scripts\\activate"
        else:
            activate_cmd = f"source {venv_dir}/bin/activate"
        print(f"To activate the virtual environment, run: {activate_cmd}")
    
    print("\nTo start the dashboard, run:")
    if venv_dir:
        if platform.system() == "Windows":
            print(f"{venv_dir}\\Scripts\\doc-evaluator-dashboard")
        else:
            print(f"{venv_dir}/bin/doc-evaluator-dashboard")
    else:
        print("doc-evaluator-dashboard")

if __name__ == "__main__":
    main()