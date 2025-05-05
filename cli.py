#!/usr/bin/env python3
"""
ODD Evaluation CLI

Command-line interface for evaluating documentation using LLM-based evaluation techniques.
"""

import argparse
import sys
import os
import yaml
import logging
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("doc_evaluator_cli")

# Import pipeline components
from pipeline.evaluation_runner import run_evaluation_pipeline

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate documentation using LLM-based techniques"
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
        help="Directory containing markdown files with documentation"
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
        default="./config/prompts.yaml",
        help="Path to the evaluation prompts YAML file"
    )
    
    parser.add_argument(
        "--section-range", 
        type=str, 
        default="1-5",
        help="Range of sections to evaluate (e.g., '1-5' or '2')"
    )
    
    parser.add_argument(
        "--config", 
        type=str,
        help="Path to a configuration YAML file"
    )
    
    parser.add_argument(
        "--model", 
        type=str,
        default=None,
        help="LLM model to use for evaluation"
    )
    
    parser.add_argument(
        "--temperature", 
        type=float,
        default=0.0,
        help="Temperature for LLM calls (0.0-1.0)"
    )
    
    parser.add_argument(
        "--max-workers", 
        type=int,
        default=4,
        help="Maximum number of parallel workers"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def parse_section_range(range_str: str) -> Tuple[int, int]:
    """
    Parse section range string to tuple.
    
    Args:
        range_str: Range string like "1-5" or "3"
        
    Returns:
        Tuple of (start, end+1)
    """
    try:
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            return (start, end + 1)  # End is inclusive
        else:
            # Single section
            section = int(range_str)
            return (section, section + 1)
    except ValueError:
        logger.warning(f"Invalid section range: {range_str}. Using default 1-5.")
        return (1, 6)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config YAML file
        
    Returns:
        Dictionary with configuration values
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        return {}

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Load config file if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Merge command line args with config file (command line takes precedence)
    yaml_dir = config.get('yaml_dir', args.yaml_dir)
    md_dir = config.get('md_dir', args.md_dir)
    output_dir = config.get('output_dir', args.output_dir)
    prompt_file = config.get('prompt_file', args.prompt_file)
    section_range_str = config.get('section_range', args.section_range)
    model = config.get('model', args.model)
    temperature = config.get('temperature', args.temperature)
    max_workers = config.get('max_workers', args.max_workers)
    
    # Parse section range
    section_range = parse_section_range(section_range_str)
    
    # Prepare model parameters
    model_params = {
        'temperature': temperature,
        'max_workers': max_workers
    }
    
    if model:
        model_params['model'] = model
    
    # Log settings
    logger.info("Starting documentation evaluation with settings:")
    logger.info(f"  YAML directory: {yaml_dir}")
    logger.info(f"  Markdown directory: {md_dir}")
    logger.info(f"  Output directory: {output_dir}")
    logger.info(f"  Prompt file: {prompt_file}")
    logger.info(f"  Section range: {section_range}")
    logger.info(f"  LLM settings: temperature={temperature}, max_workers={max_workers}")
    if model:
        logger.info(f"  LLM model: {model}")
    
    # Run the evaluation pipeline
    result_file = run_evaluation_pipeline(
        yaml_dir=yaml_dir,
        md_dir=md_dir,
        output_dir=output_dir,
        prompt_file=prompt_file,
        section_range=section_range,
        model_params=model_params
    )
    
    if result_file:
        logger.info(f"Evaluation complete. Results saved to: {result_file}")
    else:
        logger.error("Evaluation failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()