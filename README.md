# LLM-Based Documentation Evaluation Tool

## Overview

This tool provides an end-to-end pipeline for evaluating documentation quality using LLM-based assessments. It's designed to work with ODD (Object Definition Document) documentation but can be extended to other document types. The tool analyzes documentation against predefined criteria and provides quantitative scores and qualitative feedback.

## Key Features

- **Automated Documentation Evaluation**: Assess documentation quality without pre-defined ground truth
- **Multiple Evaluation Metrics**: Score coherence, quality, capture rate, and hallucination detection
- **Modular Architecture**: Easily extensible to new document types and evaluation criteria
- **Parallel Processing**: Efficient processing of multiple documents and sections
- **Excel Report Generation**: Detailed reports with scores and feedback

## Directory Structure

```
├── evaluation_pipeline.py      # Main pipeline implementation
├── llm_adapter.py              # Adapter for LLM API calls
├── cli.py                      # Command-line interface
├── config/
│   ├── prompts.yaml            # Evaluation prompts for LLM
│   ├── odd1.yaml               # Section 1 questions
│   ├── odd2.yaml               # Section 2 questions
│   └── ...
├── examples/
│   ├── ODD_Section_1_short.md  # Example ODD documentation
│   ├── ODD_Section_2_short.md
│   └── ...
└── evaluation_results/         # Output directory for results
    ├── Section1_eval.xlsx
    ├── Section2_eval.xlsx
    └── merged_evaluation.xlsx
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/llm-doc-evaluator.git
cd llm-doc-evaluator
```

2. Set up a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

1. Prepare your documentation files in markdown format (see examples directory)
2. Prepare your question YAML files (see config directory)
3. Run the evaluation:

```bash
python cli.py --yaml-dir ./config --md-dir ./examples --output-dir ./evaluation_results
```

## Detailed Usage

### Command Line Interface

The CLI provides various options for customizing the evaluation:

```bash
python cli.py --help
```

Options:

- `--yaml-dir`: Directory containing YAML files with questions (default: "./")
- `--md-dir`: Directory containing markdown files with documentation (default: "./")
- `--output-dir`: Directory for saving evaluation results (default: "./evaluation_results")
- `--prompt-file`: Path to evaluation prompts YAML file (default: "./prompts.yaml")
- `--section-range`: Range of sections to evaluate (e.g., '1-5' or '2-3') (default: "1-5")
- `--config`: Path to a configuration YAML file (optional)

### Configuration Files

#### Evaluation Prompts (prompts.yaml)

This file defines the prompts used to evaluate different aspects of the documentation:

```yaml
evaluation_prompts:
  - section: "1. Coherence/Clarity"
    description: "Evaluate if the output is clear and coherent."
    prompt: |
      Evaluate the following output for coherence and clarity:
      Output: {output}
      ...
```

#### Question Files (oddX.yaml)

These files define the questions and sections for evaluation:

```yaml
- section: "Object Scope, Purpose, and Use"
  prompt: |
    Describe the overall scope, purpose, and intended use of the AI component or module.
```

### Using the Python API

You can also use the evaluation pipeline directly in your Python code:

```python
from evaluation_pipeline import run_evaluation_pipeline

run_evaluation_pipeline(
    yaml_dir="./config",
    md_dir="./examples",
    output_dir="./results",
    prompt_file="./config/prompts.yaml",
    section_range=(1, 6)  # Evaluate sections 1-5
)
```

## Understanding the Evaluation Metrics

The tool evaluates documentation using four key metrics:

1. **Coherence/Clarity Score (0-1)**

   - How clear, understandable, and logically structured the content is

2. **Quality Score (0-1)**

   - How well the content addresses the specific requirements

3. **Capture Rate (0-1)**

   - The percentage of required information that is included

4. **Hallucination Score (0-1)**
   - Whether the content contains fabricated or unsubstantiated information
   - Lower is better (0 = no hallucinations)

## Creating Custom Evaluation Criteria

To create custom evaluation criteria:

1. Modify the `prompts.yaml` file to include your new criteria
2. Update the `evaluation_pipeline.py` file to include new evaluation methods
3. Extend the `AnswerEvaluation` class to include your new result types

## Examples

The `examples` directory contains sample ODD documentation to demonstrate the tool's capabilities.

## Extending the Tool

The modular design makes it easy to extend the tool for other document types:

1. Create new YAML files for your document sections
2. Modify the extraction logic if needed
3. Update evaluation prompts for domain-specific criteria

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
