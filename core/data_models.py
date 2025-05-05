# core/data_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from enum import Enum

class EvaluationMetric(str, Enum):
    COHERENCE = "coherence"
    QUALITY = "quality"
    CAPTURE = "capture"
    HALLUCINATION = "hallucination"

class EvaluationResult(BaseModel):
    """Base class for individual evaluation results."""
    score: float = Field(..., ge=0.0, le=1.0)
    comment: str
    
class DocumentSection(BaseModel):
    """Represents a section of documentation."""
    section_id: str
    title: str
    content: str
    requirements: Optional[List[str]] = None

class EvaluationReport(BaseModel):
    """Complete evaluation for a document section."""
    section: DocumentSection
    metrics: Dict[EvaluationMetric, EvaluationResult]
    
    def average_score(self) -> float:
        """Calculate average score across all metrics."""
        scores = [r.score for r in self.metrics.values()]
        return sum(scores) / len(scores) if scores else 0.0
