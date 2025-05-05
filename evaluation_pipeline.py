import os
import shutil
import pandas as pd
import yaml
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from pydantic import BaseModel

# Define Evaluation Result Models
class EvaluationResult(BaseModel):
    """Base class for individual evaluation results."""
    score: float
    comment: str

class CoherenceClarityResult(EvaluationResult):
    """Result for coherence and clarity evaluation."""
    pass

class QualityEvaluationResult(EvaluationResult):
    """Result for quality evaluation."""
    pass

class CaptureEvaluationResult(EvaluationResult):
    """Result for capture rate evaluation."""
    pass

class HallucinationEvaluationResult(EvaluationResult):
    """Result for hallucination detection."""
    pass

class AnswerEvaluation(BaseModel):
    """Aggregate result containing all evaluation aspects."""
    coherence_clarity: CoherenceClarityResult
    quality: QualityEvaluationResult
    capture: CaptureEvaluationResult
    hallucination: HallucinationEvaluationResult

# Utility Functions
def yaml_to_csv(yaml_data: dict, csv_file: str) -> None:
    """Convert YAML data to a CSV file with proper structure."""
    # Create DataFrame from YAML data
    rows = []
    for item in yaml_data:
        section = item.get('section', '')
        prompt = item.get('prompt', '')
        rows.append({
            'Section': section,
            'Question': prompt,
            'Requirements': '',  # Will be filled later
            'Answer': '',  # Will be filled from markdown
            'Coherence/Clarity Score': '',
            'Quality Score': '',
            'Capture Rate': '',
            'Hallucination Score': ''
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False)
    print(f"CSV file created: {csv_file}")

def generate_guidelines(csv_file: str) -> None:
    """Generate guidelines for each question in the CSV file."""
    try:
        df = pd.read_csv(csv_file)
        # For each row, generate requirements based on the question
        for idx, row in df.iterrows():
            question = row['Question']
            section = row['Section']
            
            # Generate simple requirements (this is a placeholder - replace with actual LLM call)
            requirements = [
                f"Provide clear information about {section}",
                f"Address all aspects mentioned in the question"
            ]
            
            # Update the CSV file with requirements
            df.at[idx, 'Requirements'] = "\n".join(requirements)
        
        df.to_csv(csv_file, index=False)
        print(f"Guidelines generated for {csv_file}")
    except Exception as e:
        print(f"Error generating guidelines: {e}")

def match_answers(md_content: str, csv_file: str) -> None:
    """Extract answers from markdown file and match them to questions in CSV."""
    try:
        df = pd.read_csv(csv_file)
        
        # Extract sections and their content from markdown
        section_pattern = r"## (.+?)\n(.*?)(?=\n## |\Z)"
        matches = re.finditer(section_pattern, md_content, re.DOTALL)
        
        section_content = {}
        for match in matches:
            section_title = match.group(1).strip()
            content = match.group(2).strip()
            section_content[section_title] = content
        
        # Match sections to questions in the CSV file
        for idx, row in df.iterrows():
            section = row['Section']
            if section in section_content:
                df.at[idx, 'Answer'] = section_content[section]
            else:
                # Try to find partial matches
                for md_section, content in section_content.items():
                    if section in md_section or md_section in section:
                        df.at[idx, 'Answer'] = content
                        break
        
        df.to_csv(csv_file, index=False)
        print(f"Answers matched in {csv_file}")
    except Exception as e:
        print(f"Error matching answers: {e}")

# Load YAML Prompts
def load_prompts(yaml_path: str) -> Dict[str, str]:
    """Load evaluation prompts from the YAML file."""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        if 'evaluation_prompts' in data:
            return {section['section']: section['prompt'] for section in data['evaluation_prompts']}
        else:
            return {}
    except Exception as e:
        print(f"Error loading prompts: {e}")
        return {}

# Helper function to load YAML files
def load_yaml_file(file_path: str) -> dict:
    """Load a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {file_path}: {e}")
        return {}

# LLM Connector (Placeholder)
def generate_content(prompt: str) -> str:
    """Placeholder for LLM API call - replace with actual implementation."""
    # This should call your LLM service
    return "Score: 0.85\nThis response demonstrates good coherence and clarity."

# Evaluator Class
class DgenEvalWithLLM:
    """Evaluator class that uses an LLM for scoring answers based on guidelines and context."""
    def __init__(self, context: str, prompts: Dict[str, str]):
        self.context = context
        self.prompts = prompts

    def parse_llm_response(self, response_text: str) -> Dict[str, any]:
        """Parse LLM response text to extract score and comment."""
        match = re.search(r'\b(\d(\.\d+)?)\b', response_text)
        score = float(match.group(1)) if match else 0.0
        return {"score": score, "comment": response_text.strip()}

    def evaluate_coherence_clarity(self, output: str) -> CoherenceClarityResult:
        """Evaluate coherence and clarity."""
        if "1. Coherence/Clarity" not in self.prompts:
            return CoherenceClarityResult(score=0.0, comment="No coherence prompt available")
            
        prompt = self.prompts["1. Coherence/Clarity"].format(output=output)
        response = self.parse_llm_response(generate_content(prompt))
        return CoherenceClarityResult(score=response['score'], comment=response['comment'])

    def evaluate_quality(self, output: str, requirements: str) -> QualityEvaluationResult:
        """Evaluate quality rate."""
        if "2. Quality Rate" not in self.prompts:
            return QualityEvaluationResult(score=0.0, comment="No quality prompt available")
            
        prompt = self.prompts["2. Quality Rate"].format(output=output, requirements=requirements)
        response = self.parse_llm_response(generate_content(prompt))
        return QualityEvaluationResult(score=response['score'], comment=response['comment'])

    def evaluate_capture(self, output: str, requirements: str) -> CaptureEvaluationResult:
        """Evaluate capture rate."""
        if "3. Capture Rate" not in self.prompts:
            return CaptureEvaluationResult(score=0.0, comment="No capture prompt available")
            
        prompt = self.prompts["3. Capture Rate"].format(output=output, requirements=requirements)
        response = self.parse_llm_response(generate_content(prompt))
        return CaptureEvaluationResult(score=response['score'], comment=response['comment'])

    def evaluate_hallucinations(self, output: str, requirements: str) -> HallucinationEvaluationResult:
        """Evaluate hallucination rate."""
        if "4. Hallucination Rate" not in self.prompts:
            return HallucinationEvaluationResult(score=0.0, comment="No hallucination prompt available")
            
        prompt = self.prompts["4. Hallucination Rate"].format(output=output, requirements=requirements)
        response = self.parse_llm_response(generate_content(prompt))
        return HallucinationEvaluationResult(score=response['score'], comment=response['comment'])

    def evaluate_answer(self, output: str, requirements: str) -> AnswerEvaluation:
        """Perform a complete evaluation of the output."""
        coherence_clarity_result = self.evaluate_coherence_clarity(output)
        quality_result = self.evaluate_quality(output, requirements)
        capture_result = self.evaluate_capture(output, requirements)
        hallucination_result = self.evaluate_hallucinations(output, requirements)

        return AnswerEvaluation(
            coherence_clarity=coherence_clarity_result,
            quality=quality_result,
            capture=capture_result,
            hallucination=hallucination_result
        )

def evaluate_answers(csv_file: str, prompts_path: str = "evaluation_prompts.yaml"):
    """Evaluate answers in the CSV file using the DgenEvalWithLLM class."""
    try:
        # Load evaluation prompts
        prompts = load_prompts(prompts_path)
        
        if not prompts:
            print(f"Warning: No evaluation prompts found at {prompts_path}")
            # Use default prompts as fallback
            prompts = {
                "1. Coherence/Clarity": "Evaluate the following output for coherence and clarity:\nOutput: {output}\nProvide a score between 0 and 1.",
                "2. Quality Rate": "Evaluate the quality of the following output:\nOutput: {output}\nRequirements: {requirements}\nProvide a score between 0 and 1.",
                "3. Capture Rate": "Evaluate the capture rate of the following output:\nOutput: {output}\nRequirements: {requirements}\nProvide a score between 0 and 1.",
                "4. Hallucination Rate": "Evaluate the hallucination rate of the following output:\nOutput: {output}\nRequirements: {requirements}\nProvide a score between 0 and 1."
            }
        
        # Create evaluator
        evaluator = DgenEvalWithLLM(context="", prompts=prompts)
        
        # Load CSV file
        df = pd.read_csv(csv_file)
        
        # Evaluate each answer
        for idx, row in df.iterrows():
            answer = row['Answer']
            requirements = row['Requirements']
            
            if pd.isna(answer) or not answer:
                continue
                
            # Evaluate answer
            evaluation = evaluator.evaluate_answer(answer, requirements)
            
            # Update CSV with evaluation results
            df.at[idx, 'Coherence/Clarity Score'] = evaluation.coherence_clarity.score
            df.at[idx, 'Quality Score'] = evaluation.quality.score
            df.at[idx, 'Capture Rate'] = evaluation.capture.score
            df.at[idx, 'Hallucination Score'] = evaluation.hallucination.score
        
        # Save updated CSV file
        df.to_csv(csv_file, index=False)
        print(f"Answers evaluated in {csv_file}")
    except Exception as e:
        print(f"Error evaluating answers: {e}")

# Function to process a single section
def process_section(section_no, yaml_dir, md_dir, output_dir, prompt_file):
    try:
        # Stage 1: Create CSV file from YAML
        yaml_file = os.path.join(yaml_dir, f"odd{section_no}.yaml")
        
        if not os.path.exists(yaml_file):
            print(f"YAML file not found: {yaml_file}")
            return
            
        with open(yaml_file, "r", encoding="utf-8") as yf:
            yaml_data = yaml.safe_load(yf)

        # Make sure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create CSV file path
        csv_file = os.path.join(output_dir, f"Section{section_no}_questions_and_guidelines.csv")
        yaml_to_csv(yaml_data, csv_file=csv_file)

        # Generate guidelines
        generate_guidelines(csv_file)

        # Stage 2: Include answers and append with calculated metrics
        q_file = csv_file
        eval_file = os.path.join(output_dir, f"Section{section_no}_eval.csv")
        shutil.copyfile(q_file, eval_file)

        markdown_file = os.path.join(md_dir, f"ODD_Section_{section_no}_short.md")
        
        if not os.path.exists(markdown_file):
            print(f"Markdown file not found: {markdown_file}")
            return
            
        # Process markdown file and evaluate answers
        with open(markdown_file, "r", encoding="utf-8") as md_file:
            md_content = md_file.read()
            
        match_answers(md_content, eval_file)
        evaluate_answers(eval_file, prompt_file)

    except Exception as e:
        print(f"Error processing Section {section_no}: {e}")

# Function to merge evaluation files into a single CSV file
def merge_evaluation_files(output_dir, merged_output_file):
    merged_data = []

    for section_no in range(1, 6):
        eval_file = os.path.join(output_dir, f"Section{section_no}_eval.csv")
        if os.path.exists(eval_file):
            try:
                df = pd.read_csv(eval_file)
                df.insert(0, "Section #", section_no)
                merged_data.append(df)
            except Exception as e:
                print(f"Error reading {eval_file}: {e}")

    if merged_data:
        try:
            merged_df = pd.concat(merged_data, ignore_index=True)
            merged_df.to_csv(merged_output_file, index=False)
            print(f"Merged data saved to {merged_output_file}")
        except Exception as e:
            print(f"Error saving merged file: {e}")
    else:
        print("No evaluation files found to merge.")

# Main pipeline function
def run_evaluation_pipeline(yaml_dir="./config", md_dir="./examples", output_dir="./evaluation_results", 
                           prompt_file="./config/prompts.yaml", section_range=(1, 6)):
    """
    Run the complete evaluation pipeline.
    
    Args:
        yaml_dir: Directory containing YAML question files
        md_dir: Directory containing markdown documentation files
        output_dir: Directory for saving evaluation results
        prompt_file: Path to the evaluation prompts YAML file
        section_range: Tuple of (start, end+1) section numbers to evaluate
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process each section
    for section_no in range(section_range[0], section_range[1]):
        process_section(section_no, yaml_dir, md_dir, output_dir, prompt_file)
    
    # Merge all evaluation files
    merged_output_file = os.path.join(output_dir, "merged_evaluation.csv")
    merge_evaluation_files(output_dir, merged_output_file)
    
    print(f"Evaluation pipeline completed. Results saved to {output_dir}")
    return merged_output_file

# Main execution
if __name__ == "__main__":
    run_evaluation_pipeline()