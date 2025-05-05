# llm/parsers.py
import re
from typing import List, Dict, Any
from core.data_models import EvaluationResult

def parse_llm_evaluation_response(response: str) -> EvaluationResult:
    """
    Parse LLM response to extract score and comment.
    
    Args:
        response: The raw LLM response text
        
    Returns:
        EvaluationResult with extracted score and comment
    """
    # Extract score (look for number between 0-1 with optional decimal)
    score_match = re.search(r'\b(0(\.\d+)?|1(\.0+)?)\b', response)
    score = float(score_match.group(1)) if score_match else 0.0
    
    # Clean up response to use as comment
    comment = response.strip()
    
    return EvaluationResult(score=score, comment=comment)

def extract_requirements_from_llm(response: str) -> List[str]:
    """
    Extract requirements from LLM-generated text.
    
    Args:
        response: LLM response containing requirements
        
    Returns:
        List of extracted requirements
    """
    # Look for lines starting with common list markers
    pattern = r'(?:^|\n)(?:[-*•]|\d+\.)\s*(.+?)(?=\n[-*•]|\n\d+\.|\n\n|\Z)'
    matches = re.finditer(pattern, response, re.MULTILINE)
    
    requirements = [match.group(1).strip() for match in matches]
    
    # If no list items found, split by newlines
    if not requirements:
        requirements = [line.strip() for line in response.split('\n') if line.strip()]
    
    return requirements
