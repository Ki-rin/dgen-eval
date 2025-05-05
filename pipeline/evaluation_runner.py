# pipeline/evaluation_runner.py
import os
import logging
import concurrent.futures  # Added this import
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from core.data_models import DocumentSection, EvaluationReport, EvaluationMetric, EvaluationResult
from evaluators.base_evaluator import BaseEvaluator
from evaluators.llm_evaluator import LLMEvaluator
from llm.prompts import load_prompts
from pipeline.document_processors import extract_sections, generate_requirements
from pipeline.reporting import create_csv_report

logger = logging.getLogger(__name__)

class EvaluationPipeline:
    """Main pipeline for document evaluation."""
    
    def __init__(
        self, 
        evaluator: BaseEvaluator,
        output_dir: str,
        max_workers: int = 4
    ):
        self.evaluator = evaluator
        self.output_dir = output_dir
        self.max_workers = max_workers
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def run_evaluation(
        self,
        yaml_dir: str,
        md_dir: str,
        section_range: Tuple[int, int],
    ) -> str:
        """Run the evaluation pipeline on specified sections."""
        all_reports = []
        
        # Process each section
        with ThreadPoolExecutor(max_workers=min(self.max_workers, section_range[1] - section_range[0])) as executor:
            future_to_section = {
                executor.submit(self._process_section, section_num, yaml_dir, md_dir): section_num
                for section_num in range(section_range[0], section_range[1])
            }
            
            for future in concurrent.futures.as_completed(future_to_section):
                section_num = future_to_section[future]
                try:
                    section_reports = future.result()
                    if section_reports:
                        all_reports.extend(section_reports)
                except Exception as e:
                    logger.error(f"Error processing section {section_num}: {e}")
        
        # Generate merged report
        if all_reports:
            merged_file = os.path.join(self.output_dir, "merged_evaluation.csv")
            create_csv_report(all_reports, merged_file)
            return merged_file
        
        return None
    
    def _process_section(self, section_num: int, yaml_dir: str, md_dir: str) -> List[EvaluationReport]:
        """Process a single section and return evaluation reports."""
        try:
            # Extract sections and requirements
            yaml_file = os.path.join(yaml_dir, f"odd{section_num}.yaml")
            md_file = os.path.join(md_dir, f"ODD_Section_{section_num}_short.md")
            
            if not os.path.exists(yaml_file) or not os.path.exists(md_file):
                logger.warning(f"Files not found for section {section_num}")
                return []
            
            # Extract sections from documents
            sections = extract_sections(yaml_file, md_file)
            
            # Generate requirements if needed
            sections_with_requirements = [
                generate_requirements(section) if not section.requirements else section
                for section in sections
            ]
            
            # Evaluate each section
            reports = []
            for section in sections_with_requirements:
                evaluation_results = self.evaluator.evaluate_section(section)
                report = EvaluationReport(section=section, metrics=evaluation_results)
                reports.append(report)
            
            # Create section report file
            if reports:
                section_file = os.path.join(self.output_dir, f"Section{section_num}_eval.csv")
                create_csv_report(reports, section_file)
            
            return reports
            
        except Exception as e:
            logger.error(f"Error in section {section_num}: {e}")
            return []

# Main entry point function
def run_evaluation_pipeline(
    yaml_dir: str = "./config",
    md_dir: str = "./examples",
    output_dir: str = "./evaluation_results",
    prompt_file: str = "./config/prompts.yaml",
    section_range: Tuple[int, int] = (1, 6),
    model_params: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Run the document evaluation pipeline.
    
    Args:
        yaml_dir: Directory containing YAML question files
        md_dir: Directory containing markdown documentation files
        output_dir: Directory for saving evaluation results
        prompt_file: Path to the evaluation prompts YAML file
        section_range: Tuple of (start, end+1) section numbers to evaluate
        model_params: LLM model parameters
        
    Returns:
        Path to the merged evaluation report or None if failed
    """
    try:
        # Load evaluation prompts
        prompts = load_prompts(prompt_file)
        if not prompts:
            logger.error(f"Failed to load prompts from {prompt_file}")
            return None
        
        # Create evaluator
        evaluator = LLMEvaluator(prompts=prompts, model_params=model_params)
        
        # Create and run pipeline
        pipeline = EvaluationPipeline(
            evaluator=evaluator,
            output_dir=output_dir,
            max_workers=model_params.get("max_workers", 4) if model_params else 4
        )
        
        return pipeline.run_evaluation(yaml_dir, md_dir, section_range)
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return None