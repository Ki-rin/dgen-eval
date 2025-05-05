# Documentation Evaluation System

A modular system for evaluating documentation quality using LLM-based techniques. This project includes a documentation evaluation pipeline and an interactive dashboard for visualizing results.

## Features

- **Modular Architecture**: Easily extensible with new evaluation metrics and document types
- **LLM-Based Evaluation**: Uses AI models to evaluate documentation quality
- **Interactive Dashboard**: Visualize evaluation results through a Streamlit interface
- **Evaluation Metrics**:
  - Coherence: Clarity and logical flow
  - Quality: Completeness and relevance
  - Capture Rate: Percentage of requirements addressed
  - Hallucination: Detection of fabricated information
- **Support for Multiple Sections**: Process and evaluate multi-section documents
- **Parallel Processing**: Evaluate multiple sections simultaneously
- **Deployment Options**: Run locally or deploy as a service

## Project Structure

```
doc_evaluator/
├── cli.py                       # Command-line interface
├── app.py                       # Streamlit dashboard
├── dashboard.py                 # Dashboard visualization components
├── core/                        # Core functionality
│   ├── config.py                # Configuration handling
│   ├── data_models.py           # Pydantic models for results
│   └── utils.py                 # Utility functions
├── evaluators/                  # Documentation evaluators
│   ├── base_evaluator.py        # Abstract base class
│   └── llm_evaluator.py         # LLM-based evaluator
├── llm/                         # LLM integration components
│   ├── adapter.py               # LLM adapter with retry logic
│   ├── parsers.py               # Response parsing utilities
│   └── prompts.py               # Prompt management
├── pipeline/                    # Evaluation pipeline
│   ├── document_processors.py   # Document extraction/matching
│   ├── evaluation_runner.py     # Main pipeline runner
│   └── reporting.py             # Report generation
├── config/                      # Configuration files
├── examples/                    # Example documentation files
└── evaluation_results/          # Evaluation results
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Option 1: Installation from Source

1. Clone the repository:

   ```bash
   git clone https://github.com/your-org/doc-evaluator.git
   cd doc-evaluator
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Automated Installation

Use the installation script:

```bash
python install.py
```

This script:

- Creates a virtual environment
- Installs dependencies
- Sets up initial directories and sample data

## Usage

### 1. Command Line Interface (CLI)

The CLI allows you to run evaluations from the command line:

```bash
# Basic usage
python cli.py --yaml-dir ./config --md-dir ./examples --output-dir ./evaluation_results

# With model parameters
python cli.py --yaml-dir ./config --md-dir ./examples --model "your-model-name" --temperature 0.1

# Using a config file
python cli.py --config ./evaluation_config.yaml

# Evaluating specific sections
python cli.py --section-range 2-4
```

### 2. Running the Dashboard

#### Option 1: Using the script

```bash
./run_dashboard.sh
```

This script:

- Creates a virtual environment if needed
- Installs required dependencies
- Offers to run evaluations to generate/update results
- Starts the Streamlit dashboard

#### Option 2: Directly with Streamlit

```bash
streamlit run app.py
```

The dashboard will be available at http://localhost:8501 in your web browser.

### 3. Python API

You can also use the evaluation pipeline in your Python code:

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

## Service Deployment

### Docker Deployment

1. Build the Docker image:

   ```bash
   docker build -t doc-evaluator:latest -f deployment/Dockerfile .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 -v ./config:/app/config -v ./examples:/app/examples -v ./evaluation_results:/app/evaluation_results doc-evaluator:latest
   ```

Alternatively, use Docker Compose:

```bash
docker-compose -f deployment/docker-compose.yaml up
```

### OpenShift Deployment

1. Configure your OpenShift environment in the `deploy-script.sh`:

   ```bash
   # Edit these variables
   PROJECT_NAME="doc-evaluator"
   IMAGE_REPOSITORY="your-registry.example.com"
   IMAGE_TAG="latest"
   STORAGE_CLASS_NAME="standard"
   ```

2. Run the deployment script:
   ```bash
   chmod +x deployment/deploy-script.sh
   ./deployment/deploy-script.sh
   ```

This script:

- Creates/switches to the specified project
- Builds and pushes the container image
- Creates persistent volume claims
- Deploys the application
- Configures a route for external access

#### Deployment Configuration

The deployment uses:

- A Deployment object with 1 replica (can be scaled)
- A Service for internal networking
- A Route for external access
- Three Persistent Volume Claims:
  - `doc-evaluator-config-pvc`: For configuration files
  - `doc-evaluator-examples-pvc`: For example documents
  - `doc-evaluator-results-pvc`: For evaluation results

## Dashboard Features

The dashboard has two main views:

1. **Dashboard View** - Shows summary statistics and visualizations:

   - Overview of average scores for each metric
   - Overall documentation score
   - Comparison charts for all metrics
   - Heatmap comparing sections across metrics
   - Areas for improvement

2. **Section Details View** - Shows detailed information for each section:
   - Original documentation content
   - Requirements for the section
   - Evaluation results with scores and comments for each metric

## Customization

### Configuration

Edit `evaluation_config.yaml` to customize:

- Input/output directories
- Section range to evaluate
- LLM model parameters
- Dashboard settings

```yaml
# Example configuration
yaml_dir: "./config"
md_dir: "./examples"
output_dir: "./evaluation_results"
prompt_file: "./config/prompts.yaml"
section_range: "1-3"

model_params:
  temperature: 0.0
  max_workers: 4
  # model: "your-model-name"  # Uncomment and set if needed
```

### Adding Custom Evaluation Metrics

1. Update `core/data_models.py` to include your new metric
2. Add evaluation method to the `BaseEvaluator` class
3. Implement the method in your evaluator
4. Update prompt templates in `llm/prompts.py` or `config/prompts.yaml`

### Extending for New Document Types

1. Create YAML files for your document sections in the `config/` directory
2. Update the document extraction logic in `pipeline/document_processors.py` if needed
3. Create appropriate prompts for evaluation

## Troubleshooting

- **Missing Sections**: Check that YAML and markdown section titles match exactly or use fuzzy matching
- **LLM API Issues**: Check the adapter logs and retry logic
- **Low Scores**: Review the generated requirements for clarity and specificity
- **Performance Issues**: Adjust max_workers and batch processing parameters
- **Dashboard Not Starting**: Ensure Streamlit is installed and ports are available

## License

This project is licensed under the MIT License - see the LICENSE file for details.
