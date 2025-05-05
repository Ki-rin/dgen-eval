# evaluators/llm_evaluator.py
from typing import Dict, List, Optional, Any
from core.data_models import DocumentSection, EvaluationResult, EvaluationMetric
from evaluators.base_evaluator import BaseEvaluator
from llm.adapter import call_llm
from llm.parsers import parse_llm_evaluation_response
from llm.prompts import get_evaluation_prompt

class LLMEvaluator(BaseEvaluator):
    """LLM-based document evaluator."""
    
    def __init__(self, prompts: Dict[str, str], model_params: Optional[Dict[str, Any]] = None):
        self.prompts = prompts
        self.model_params = model_params or {}
    
    def evaluate_section(self, section: DocumentSection) -> Dict[EvaluationMetric, EvaluationResult]:
        """Evaluate all aspects of a document section."""
        requirements_text = "\n".join(section.requirements) if section.requirements else ""
        
        return {
            EvaluationMetric.COHERENCE: self.evaluate_coherence(section.content),
            EvaluationMetric.QUALITY: self.evaluate_quality(section.content, requirements_text),
            EvaluationMetric.CAPTURE: self.evaluate_capture(section.content, requirements_text),
            EvaluationMetric.HALLUCINATION: self.evaluate_hallucination(section.content, requirements_text)
        }
    
    def evaluate_coherence(self, content: str) -> EvaluationResult:
        """Evaluate coherence using LLM."""
        prompt = get_evaluation_prompt("coherence", content=content)
        response = call_llm(prompt, **self.model_params)
        return parse_llm_evaluation_response(response)
    
    def evaluate_quality(self, content: str, requirements: str) -> EvaluationResult:
        """Evaluate quality using LLM."""
        prompt = get_evaluation_prompt("quality", content=content, requirements=requirements)
        response = call_llm(prompt, **self.model_params)
        return parse_llm_evaluation_response(response)
    
    def evaluate_capture(self, content: str, requirements: str) -> EvaluationResult:
        """Evaluate capture rate using LLM."""
        prompt = get_evaluation_prompt("capture", content=content, requirements=requirements)
        response = call_llm(prompt, **self.model_params)
        return parse_llm_evaluation_response(response)
    
    def evaluate_hallucination(self, content: str, requirements: str) -> EvaluationResult:
        """Evaluate hallucination rate using LLM."""
        prompt = get_evaluation_prompt("hallucination", content=content, requirements=requirements)
        response = call_llm(prompt, **self.model_params)
        return parse_llm_evaluation_response(response)
