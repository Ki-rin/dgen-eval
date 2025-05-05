#!/usr/bin/env python3
"""
ODD Evaluation CLI

This script provides a command-line interface for evaluating ODD (Object Definition Document)
documentation using LLM-based evaluation techniques.
"""

import argparse
import os
import sys
import yaml
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the evaluation pipeline
from evaluation_pipeline import (
    load_yaml_file,
    run_evaluation_pipeline
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate ODD documentation using LLM-based techniques"
    )
    
    parser.add_argument(
        "--yaml-dir", 
        type=str, 
        default="./config",
        help="Directory containing YAML files with questions"
    )
    
    parser.add_argument(
        "--md-dir", 
        type=str, 
        default="./examples",
        help="Directory containing markdown files with ODD documentation"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./evaluation_results",
        help="Directory for saving evaluation results"
    )
    
    parser.add_argument(
        "--prompt-file", 
        type=str, 
        default="./prompts.yaml",
        help="Path to the evaluation prompts YAML file"
    )
    
    parser.add_argument(
        "--section-range", 
        type=str, 
        default="1-5",
        help="Range of sections to evaluate (e.g., '1-5' or '2-3')"
    )
    
    parser.add_argument(
        "--config", 
        type=str,
        help="Path to a configuration YAML file"
    )

    parser.add_argument(
        "--output-format",
        type=str,
        default="csv",
        choices=["csv"],
        help="Output format for evaluation results (currently only CSV is supported)"
    )
    
    return parser.parse_args()

def parse_section_range(range_str: str) -> tuple:
    """Parse section range string (e.g., '1-5') into a tuple (start, end+1)."""
    try:
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            return (start, end + 1)  # End is inclusive, so add 1
        else:
            # Single section
            section = int(range_str)
            return (section, section + 1)
    except ValueError:
        print(f"Invalid section range: {range_str}. Using default 1-5.")
        return (1, 6)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    try:
        return load_yaml_file(config_path)
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        return {}

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # If config file is provided, load settings from it
    if args.config:
        config = load_config(args.config)
        
        yaml_dir = config.get('yaml_dir', args.yaml_dir)
        md_dir = config.get('md_dir', args.md_dir)
        output_dir = config.get('output_dir', args.output_dir)
        prompt_file = config.get('prompt_file', args.prompt_file)
        section_range_str = config.get('section_range', args.section_range)
    else:
        yaml_dir = args.yaml_dir
        md_dir = args.md_dir
        output_dir = args.output_dir
        prompt_file = args.prompt_file
        section_range_str = args.section_range
    
    section_range = parse_section_range(section_range_str)
    
    print(f"Evaluating ODD documentation with settings:")
    print(f"  YAML directory: {yaml_dir}")
    print(f"  Markdown directory: {md_dir}")
    print(f"  Output directory: {output_dir}")
    print(f"  Prompt file: {prompt_file}")
    print(f"  Section range: {section_range}")
    print(f"  Output format: CSV")
    
    # Run the evaluation pipeline
    result_file = run_evaluation_pipeline(
        yaml_dir=yaml_dir,
        md_dir=md_dir,
        output_dir=output_dir,
        prompt_file=prompt_file,
        section_range=section_range
    )
    
    print(f"Evaluation complete. Final results saved to: {result_file}")

if __name__ == "__main__":
    main()