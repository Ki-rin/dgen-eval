#!/usr/bin/env python3
"""
Initialization script for documentation evaluation environment.
Creates necessary directories and sample evaluation results.
"""

import os
import pandas as pd
import random
import json
import yaml
from datetime import datetime
import argparse

def create_directory_structure():
    """Create the necessary directory structure."""
    dirs = ["config", "examples", "evaluation_results"]
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")

def generate_sample_results(num_sections=3):
    """
    Generate sample evaluation results if real ones don't exist.
    
    Args:
        num_sections: Number of sections to generate results for
    """
    results_dir = "evaluation_results"
    
    # Check if files already exist
    existing_files = [f for f in os.listdir(results_dir) if f.endswith("_eval.csv")]
    if existing_files:
        print(f"Evaluation results already exist: {existing_files}")
        return
        
    # Create sample results for each section
    print("Generating sample evaluation results...")
    
    for section_num in range(1, num_sections + 1):
        # Try to read the markdown file to get real section titles
        section_titles = []
        md_path = os.path.join("examples", f"ODD_Section_{section_num}_short.md")
        
        if os.path.exists(md_path):
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract section titles
                import re
                section_pattern = r'## (.+?)\n'
                matches = re.finditer(section_pattern, content)
                section_titles = [match.group(1).strip() for match in matches]
            except Exception as e:
                print(f"Error reading markdown file: {e}")
                
        # If no titles found, use generic ones
        if not section_titles:
            if section_num == 1:
                section_titles = ["Object Scope, Purpose, and Use", 
                                 "1.1. Objectives and Business Purpose", 
                                 "1.2. Business Scope of the Object"]
            elif section_num == 2:
                section_titles = ["Data Scope and Feature Engineering", 
                                 "2.1. Data Sources and Collection", 
                                 "2.2. Feature Engineering and Selection",
                                 "2.3. Data Quality Checks"]
            elif section_num == 3:
                section_titles = ["Model Development", 
                                 "3.1. Model Architecture", 
                                 "3.2. Training Methodology",
                                 "3.3. Model Evaluation"]
            else:
                section_titles = [f"Section {section_num}.{i}" for i in range(1, 4)]
        
        # Generate random scores for each section
        rows = []
        for i, title in enumerate(section_titles):
            # Generate more realistic scores with some variation
            coherence = round(random.uniform(0.65, 0.95), 2)
            quality = round(random.uniform(0.6, 0.9), 2)
            capture = round(random.uniform(0.7, 0.95), 2)
            hallucination = round(random.uniform(0.1, 0.4), 2)  # Lower is better
            
            # Get content from file or use placeholder
            content = "Sample content for this section."
            requirements = "Sample requirements for this section."
            
            try:
                # Try to extract actual content
                if os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                        
                    # Look for this section's content
                    import re
                    section_pattern = f'## {re.escape(title)}\n(.*?)(?=\n## |\Z)'
                    match = re.search(section_pattern, md_content, re.DOTALL)
                    if match:
                        content = match.group(1).strip()
                
                # Try to extract requirements from YAML
                yaml_path = os.path.join("config", f"odd{section_num}.yaml")
                if os.path.exists(yaml_path):
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        yaml_data = yaml.safe_load(f)
                        
                    for item in yaml_data:
                        if item.get('section') == title and 'prompt' in item:
                            requirements = item['prompt']
                            break
            except Exception as e:
                print(f"Error extracting content/requirements: {e}")
            
            # Create sample comments
            comments = {
                "Coherence": [
                    "The content is well-structured and flows logically.",
                    "Generally clear but some transitions could be improved.",
                    "Terminology is used consistently throughout.",
                    "Good logical flow but a few sections could be more cohesive."
                ],
                "Quality": [
                    "The content addresses most requirements with good detail.",
                    "Comprehensive coverage of the topic with necessary details.",
                    "Content is relevant but could include more specific examples.",
                    "Good coverage but some areas could be expanded further."
                ],
                "Capture": [
                    "Most key requirements are addressed in the content.",
                    "Approximately 85% of requirements are fully addressed.",
                    "The content captures essential elements but misses some details.",
                    "Good coverage of requirements with minor omissions."
                ],
                "Hallucination": [
                    "No significant hallucinations detected.",
                    "Content aligns well with requirements with minimal fabrication.",
                    "A few minor statements could be more precisely worded.",
                    "Overall factual with very limited unsubstantiated claims."
                ]
            }
            
            row = {
                'Section ID': f"section_{i+1}",
                'Section Title': title,
                'Content': content,
                'Requirements': requirements,
                'Coherence Score': coherence,
                'Quality Score': quality,
                'Capture Rate': capture,
                'Hallucination Score': hallucination,
                'Coherence Comment': random.choice(comments["Coherence"]),
                'Quality Comment': random.choice(comments["Quality"]),
                'Capture Comment': random.choice(comments["Capture"]),
                'Hallucination Comment': random.choice(comments["Hallucination"]),
                'Average Score': round((coherence + quality + capture + (1-hallucination)) / 4, 2)
            }
            rows.append(row)
        
        # Create DataFrame and save
        df = pd.DataFrame(rows)
        output_file = os.path.join(results_dir, f"Section{section_num}_eval.csv")
        df.to_csv(output_file, index=False)
        print(f"Created sample results for Section {section_num}: {output_file}")
    
    # Create merged file
    merge_sample_results(num_sections)

def merge_sample_results(num_sections):
    """
    Create a merged results file.
    
    Args:
        num_sections: Number of sections to merge
    """
    results_dir = "evaluation_results"
    all_dfs = []
    
    for section_num in range(1, num_sections + 1):
        file_path = os.path.join(results_dir, f"Section{section_num}_eval.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            all_dfs.append(df)
    
    if all_dfs:
        merged_df = pd.concat(all_dfs, ignore_index=True)
        merged_file = os.path.join(results_dir, "merged_evaluation.csv")
        merged_df.to_csv(merged_file, index=False)
        print(f"Created merged evaluation file: {merged_file}")

def main():
    parser = argparse.ArgumentParser(description="Initialize documentation evaluation environment")
    parser.add_argument("--sections", type=int, default=3, help="Number of sections to create sample results for")
    args = parser.parse_args()
    
    print("Initializing documentation evaluation environment...")
    create_directory_structure()
    generate_sample_results(args.sections)
    print("Initialization complete!")

if __name__ == "__main__":
    main()