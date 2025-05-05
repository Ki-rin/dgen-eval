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

# Documentation Evaluation Dashboard

A Streamlit-based dashboard for visualizing and analyzing documentation evaluation results from the Modular Documentation Evaluation System.

## Overview

This project extends the Modular Documentation Evaluation System with a user-friendly dashboard that helps visualize, navigate, and analyze documentation evaluation results. The dashboard provides:

- An overview of evaluation metrics across all documentation sections
- Detailed views of individual section evaluations
- Interactive visualizations of evaluation results
- Easy navigation between documentation sections
- Identification of areas for improvement

## Installation

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd documentation-evaluation-dashboard
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Initialize the environment (creates necessary directories and sample data if needed):
   ```bash
   python init_eval_environment.py
   ```

## Usage

### Running the Dashboard

Use the provided script to run the dashboard:

```bash
./run_dashboard.sh
```

Or run it directly with Streamlit:

```bash
streamlit run app.py
```

The dashboard will be available at http://localhost:8501 in your web browser.

### Dashboard Features

The dashboard has two main views:

1. **Dashboard View** - Shows summary statistics and visualizations across all sections:

   - Overview of average scores for each metric
   - Overall documentation score
   - Comparison charts for all metrics
   - Heatmap comparing sections across metrics
   - Areas for improvement

2. **Section Details View** - Shows detailed information for each section:
   - Original documentation content
   - Requirements for the section
   - Evaluation results with scores and comments for each metric

### Running Evaluations

To generate actual evaluation results (instead of sample data):

1. Configure your evaluation parameters in `evaluation_config.yaml` or use command-line options.
2. Run the evaluation tool:

   ```bash
   python cli.py --yaml-dir ./config --md-dir ./examples --output-dir ./evaluation_results
   ```

3. Refresh the dashboard to see the new results.

## Project Structure

```
doc_evaluator/
├── app.py                       # Main Streamlit application
├── dashboard.py                 # Dashboard visualization components
├── cli.py                       # Command-line interface
├── init_eval_environment.py     # Environment initialization script
├── run_dashboard.sh             # Dashboard runner script
├── core/                        # Core functionality
├── evaluators/                  # Documentation evaluators
├── llm/                         # LLM integration components
├── pipeline/                    # Evaluation pipeline
├── config/                      # Configuration files
├── examples/                    # Example documentation files
└── evaluation_results/          # Evaluation results
```

## Customization

### Changing Evaluation Metrics

To modify the evaluation metrics:

1. Update `core/data_models.py` with new metrics
2. Add corresponding methods to the evaluator classes
3. Update prompts in `llm/prompts.py` or `config/prompts.yaml`
4. Update the dashboard visualizations in `dashboard.py`

### Adding New Documentation Sections

To add new documentation sections:

1. Add Markdown files to the `examples/` directory
2. Add corresponding YAML files to the `config/` directory
3. Run the evaluation pipeline to generate results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
