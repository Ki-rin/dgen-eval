# Modular Documentation Evaluation System - Integration Guide

This guide explains how to integrate the modular documentation evaluation system into your project.

## 1. Project Structure

The system has been restructured into a modular architecture with the following components:

```
doc_evaluator/
├── cli.py                       # Command-line interface
├── core/
│   ├── __init__.py
│   ├── config.py                # Configuration handling
│   ├── data_models.py           # Pydantic models for results
│   └── utils.py                 # Utility functions
├── evaluators/
│   ├── __init__.py
│   ├── base_evaluator.py        # Abstract base class
│   └── llm_evaluator.py         # LLM-based evaluator
├── llm/
│   ├── __init__.py
│   ├── adapter.py               # LLM adapter with retry logic
│   ├── parsers.py               # Response parsing utilities
│   └── prompts.py               # Prompt management
├── pipeline/
│   ├── __init__.py
│   ├── document_processors.py   # Document extraction/matching
│   ├── evaluation_runner.py     # Main pipeline runner
│   └── reporting.py             # Report generation
└── setup.py                     # Package setup
```

## 2. Key Components

### 2.1 Core Models (`core/data_models.py`)

- `DocumentSection`: Represents a section of documentation with content and requirements
- `EvaluationResult`: Contains score and comments for a specific evaluation metric
- `EvaluationReport`: Aggregates all evaluation results for a section

### 2.2 LLM Adapter (`llm/adapter.py`)

- `call_llm()`: Main function to call LLM with retry logic
- `batch_process_texts()`: Process multiple prompts in parallel

### 2.3 Evaluators (`evaluators/llm_evaluator.py`)

- `LLMEvaluator`: Evaluates documentation using LLM prompts
- Methods for each evaluation metric: coherence, quality, capture, hallucination

### 2.4 Pipeline (`pipeline/evaluation_runner.py`)

- `EvaluationPipeline`: Orchestrates the entire evaluation process
- `run_evaluation_pipeline()`: Main entry point function

## 3. Integration Steps

### 3.1 Basic Usage

The simplest way to use the system is through the main function:

```python
from pipeline.evaluation_runner import run_evaluation_pipeline

# Run evaluation
result_file = run_evaluation_pipeline(
    yaml_dir="./config",
    md_dir="./examples",
    output_dir="./results",
    prompt_file="./config/prompts.yaml",
    section_range=(1, 3),
    model_params={
        "temperature": 0.0,
        "model": "your-model-name"  # Optional
    }
)

print(f"Evaluation saved to: {result_file}")
```

### 3.2 Using the Configuration System

For more flexibility, use the configuration system:

```python
from core.config import AppConfig
from pipeline.evaluation_runner import run_evaluation_pipeline

# Create config with defaults
config = AppConfig()

# Load from file
config.load_from_file("./evaluation_config.yaml")

# Update with custom values
config.update_from_args({
    "output_dir": "./custom_results",
    "section_range": "1-3"
})

# Run evaluation using config
result_file = run_evaluation_pipeline(
    yaml_dir=config.get("yaml_dir"),
    md_dir=config.get("md_dir"),
    output_dir=config.get("output_dir"),
    prompt_file=config.get("prompt_file"),
    section_range=config.get("section_range"),
    model_params=config.get("model_params")
)
```

### 3.3 Using the EvaluationPipeline Directly

For more control, you can use the EvaluationPipeline class directly:

```python
from llm.prompts import load_prompts
from evaluators.llm_evaluator import LLMEvaluator
from pipeline.evaluation_runner import EvaluationPipeline

# Load prompts
prompts = load_prompts("./config/prompts.yaml")

# Create evaluator
evaluator = LLMEvaluator(
    prompts=prompts,
    model_params={"temperature": 0.0}
)

# Create pipeline
pipeline = EvaluationPipeline(
    evaluator=evaluator,
    output_dir="./results",
    max_workers=4
)

# Run evaluation
result_file = pipeline.run_evaluation(
    yaml_dir="./config",
    md_dir="./examples",
    section_range=(1, 3)
)
```

### 3.4 Custom Evaluation Metrics

To add custom evaluation metrics:

1. Update `core/data_models.py` to include your new metric
2. Add evaluation method to the `BaseEvaluator` class
3. Implement the method in your evaluator
4. Update prompt templates in `llm/prompts.py`

Example for adding a "correctness" metric:

```python
# In core/data_models.py
class EvaluationMetric(str, Enum):
    COHERENCE = "coherence"
    QUALITY = "quality"
    CAPTURE = "capture"
    HALLUCINATION = "hallucination"
    CORRECTNESS = "correctness"  # New metric

# In evaluators/base_evaluator.py
@abstractmethod
def evaluate_correctness(self, content: str, requirements: List[str]) -> EvaluationResult:
    """Evaluate factual correctness."""
    pass

# In evaluators/llm_evaluator.py
def evaluate_correctness(self, content: str, requirements: str) -> EvaluationResult:
    """Evaluate correctness using LLM."""
    prompt = get_evaluation_prompt("correctness", content=content, requirements=requirements)
    response = call_llm(prompt, **self.model_params)
    return parse_llm_evaluation_response(response)

# In llm/prompts.py - add to the prompts dictionary
"correctness": """
    Evaluate the factual correctness of the following output:

    Output: {content}
    Requirements: {requirements}

    Check if the information is factually correct.

    Provide:
    - Score: A number between 0.0 and 1.0
    - Brief explanation identifying any incorrect information
"""
```

## 4. Command Line Usage

The CLI provides an easy way to run evaluations:

```bash
# Basic usage
python cli.py --yaml-dir ./config --md-dir ./examples --output-dir ./results

# With model parameters
python cli.py --yaml-dir ./config --md-dir ./examples --model "your-model-name" --temperature 0.1

# Using a config file
python cli.py --config ./evaluation_config.yaml

# Evaluating specific sections
python cli.py --section-range 2-4
```

## 5. Extending for New Document Types

To extend the system for new document types:

1. Create YAML files for your document sections
2. Update the document extraction logic in `pipeline/document_processors.py`
3. Create appropriate prompts for evaluation

## 6. Adding Custom LLM Integration

If you need to use a different LLM provider:

1. Update `llm/adapter.py` to use your LLM API
2. Implement custom response parsing if needed in `llm/parsers.py`

## 7. Best Practices

- Keep prompts consistent across evaluation metrics
- Use temperature=0.0 for consistent evaluations
- Adjust max_workers based on your hardware and API rate limits
- Review and validate LLM-generated requirements before evaluation
- Use the reporting module to create standardized outputs

## 8. Troubleshooting

- **Missing Sections**: Check that YAML and markdown section titles match exactly or use fuzzy matching
- **LLM API Issues**: Check the adapter logs and retry logic
- **Low Scores**: Review the generated requirements for clarity and specificity
- **Performance Issues**: Adjust max_workers and batch processing parameters
