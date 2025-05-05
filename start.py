#!/usr/bin/env python3
"""
Starter script for Documentation Evaluation Dashboard.
This script helps initialize the environment and start the Streamlit app.
"""

import os
import sys
import subprocess
import argparse

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        return False
    return True

def ensure_directory_structure():
    """Ensure the required directory structure exists."""
    required_dirs = ["config", "examples", "evaluation_results"]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ["streamlit", "pandas", "pyyaml", "altair"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        install = input("Would you like to install them now? (y/n): ").lower()
        
        if install == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Packages installed successfully.")
        else:
            print("Please install required packages before continuing.")
            return False
    
    return True

def create_sample_data():
    """Generate sample data for evaluation."""
    if not os.path.exists("init_eval_environment.py"):
        print("Warning: init_eval_environment.py not found. Cannot create sample data.")
        return
    
    # Check if there are already files in the evaluation_results directory
    if os.path.exists("evaluation_results") and os.listdir("evaluation_results"):
        print("Evaluation results already exist.")
        regenerate = input("Would you like to regenerate sample data? (y/n): ").lower()
        if regenerate != 'y':
            return
    
    print("Generating sample evaluation data...")
    subprocess.run([sys.executable, "init_eval_environment.py"])
    print("Sample data generated successfully.")

def start_streamlit():
    """Start the Streamlit application."""
    print("Starting Streamlit dashboard...")
    subprocess.run(["streamlit", "run", "app.py"])

def main():
    parser = argparse.ArgumentParser(description="Start Documentation Evaluation Dashboard")
    parser.add_argument("--no-sample-data", action="store_true", help="Skip sample data generation")
    args = parser.parse_args()
    
    print("Documentation Evaluation Dashboard Starter")
    print("=========================================")
    
    if not check_python_version():
        return
    
    ensure_directory_structure()
    
    if not check_requirements():
        return
    
    if not args.no_sample_data:
        create_sample_data()
    
    start_streamlit()

if __name__ == "__main__":
    main()