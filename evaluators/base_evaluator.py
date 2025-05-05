# evaluators/base_evaluator.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from core.data_models import DocumentSection, EvaluationResult, EvaluationMetric

class BaseEvaluator(ABC):
    """Abstract base class for document evaluators."""
    
    @abstractmethod
    def evaluate_section(self, section: DocumentSection) -> Dict[EvaluationMetric, EvaluationResult]:
        """Evaluate a document section and return results for all metrics."""
        pass
    
    @abstractmethod
    def evaluate_coherence(self, content: str) -> EvaluationResult:
        """Evaluate coherence and clarity."""
        pass
    
    @abstractmethod
    def evaluate_quality(self, content: str, requirements: List[str]) -> EvaluationResult:
        """Evaluate quality of the content."""
        pass
    
    @abstractmethod
    def evaluate_capture(self, content: str, requirements: List[str]) -> EvaluationResult:
        """Evaluate capture rate of requirements."""
        pass
    
    @abstractmethod
    def evaluate_hallucination(self, content: str, requirements: List[str]) -> EvaluationResult:
        """Evaluate hallucination rate."""
        pass