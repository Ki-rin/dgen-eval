# llm/prompts.py
import yaml
import os
from typing import Dict, Optional, Any

def load_prompts(file_path: str) -> Dict[str, str]:
    """
    Load evaluation prompts from YAML file.
    
    Args:
        file_path: Path to prompts YAML file
        
    Returns:
        Dictionary mapping prompt names to prompt templates
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        prompts = {}
        if 'evaluation_prompts' in data:
            for prompt_data in data['evaluation_prompts']:
                section = prompt_data.get('section', '')
                prompt_text = prompt_data.get('prompt', '')
                prompts[section] = prompt_text
                
        return prompts
    except Exception as e:
        print(f"Error loading prompts: {e}")
        return {}

def get_evaluation_prompt(metric: str, **kwargs) -> str:
    """
    Get the appropriate prompt for a specific evaluation metric.
    
    Args:
        metric: The metric to get a prompt for
        **kwargs: Variables to format into the prompt
        
    Returns:
        Formatted prompt string
    """
    prompts = {
        "coherence": """
            Evaluate the following output for coherence and clarity:
            
            Output: {content}
            
            Criteria:
            - Does the output maintain a clear logical flow?
            - Is it easy to understand?
            - Is terminology used consistently?
            
            Provide:
            - Score: A number between 0.0 and 1.0
            - Brief explanation for your score
        """,
        "quality": """
            Evaluate the quality of the following output:
            
            Output: {content}
            Requirements: {requirements}
            
            Criteria:
            - Does the output address all requirements?
            - Is the information accurate and relevant?
            - Is the content sufficiently detailed?
            
            Provide:
            - Score: A number between 0.0 and 1.0
            - Brief explanation for your score
        """,
        "capture": """
            Evaluate the capture rate of the following output:
            
            Output: {content}
            Requirements: {requirements}
            
            Calculate what percentage of the requirements are addressed.
            
            Provide:
            - Score: A decimal between 0.0 and 1.0 representing the capture rate
            - Brief explanation listing which requirements were captured
        """,
        "hallucination": """
            Evaluate the following output for hallucinations:
            
            Output: {content}
            Requirements: {requirements}
            
            Check if the output contains fabricated or unsubstantiated information.
            
            Provide:
            - Score: A number between 0.0 and 1.0 (0.0 = no hallucinations)
            - Brief explanation identifying specific hallucinations if any
        """
    }
    
    prompt_template = prompts.get(metric, "")
    if not prompt_template:
        return f"Error: No prompt template found for metric '{metric}'"
    
    return prompt_template.format(**kwargs)
