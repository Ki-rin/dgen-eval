#!/bin/bash
# Script to install dependencies and run the Streamlit dashboard

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
pip install streamlit

# Run evaluation to generate results (if needed)
echo "Would you like to run the evaluation to generate/update results? (y/n)"
read run_eval

if [ "$run_eval" = "y" ] || [ "$run_eval" = "Y" ]; then
    echo "Running evaluation pipeline..."
    python cli.py
fi

# Run the Streamlit app
echo "Starting Streamlit dashboard..."
streamlit run app.py