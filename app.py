#!/usr/bin/env python3
"""
Streamlit App for Documentation Evaluation Visualization

This app displays the evaluation results for the documentation sections
and allows users to view both the source content and evaluations.
"""

import streamlit as st
import os
import pandas as pd
import yaml
import re
from pathlib import Path

# Import dashboard component
try:
    from dashboard import display_dashboard
except ImportError:
    # Define minimal dashboard function if dashboard.py is not available
    def display_dashboard(results_dir):
        st.warning("Dashboard component not available. Make sure dashboard.py exists.")

# Set page config
st.set_page_config(
    page_title="Documentation Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
)

# Define paths - these can be changed to match your environment
DEFAULT_YAML_DIR = "./config"
DEFAULT_MD_DIR = "./examples"
DEFAULT_RESULTS_DIR = "./evaluation_results"

def load_markdown_file(filepath):
    """Load markdown file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading file: {e}"

def extract_sections(md_content):
    """Extract sections from markdown content."""
    section_pattern = r'## (.+?)\n(.*?)(?=\n## |\Z)'
    matches = re.finditer(section_pattern, md_content, re.DOTALL)
    
    sections = []
    for match in matches:
        section_title = match.group(1).strip()
        content = match.group(2).strip()
        sections.append({"title": section_title, "content": content})
    
    return sections

def load_yaml_requirements(filepath):
    """Load requirements from YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data
    except Exception as e:
        st.error(f"Error loading YAML file: {e}")
        return []

def load_evaluation_results(filepath):
    """Load evaluation results from CSV file."""
    try:
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            return None
    except Exception as e:
        st.error(f"Error loading evaluation results: {e}")
        return None

def display_metric_card(title, score, comment, color):
    """Display a metric card with score and comment."""
    st.markdown(f"""
    <div style="border:1px solid {color}; border-radius:5px; padding:10px; margin:5px 0;">
        <h4 style="color:{color};">{title}: {score:.2f}</h4>
        <p>{comment}</p>
    </div>
    """, unsafe_allow_html=True)

def map_score_to_color(score, inverted=False):
    """Map a score to a color (red to green)."""
    if inverted:  # For hallucination where lower is better
        score = 1.0 - score
    
    if score > 0.8:
        return "#28a745"  # Green
    elif score > 0.6:
        return "#5cb85c"  # Light green
    elif score > 0.4:
        return "#ffc107"  # Yellow
    elif score > 0.2:
        return "#ff9800"  # Orange
    else:
        return "#dc3545"  # Red

def show_section_details(yaml_dir, md_dir, results_dir):
    """Show the section details view."""
    # Get available sections
    section_files = []
    if os.path.exists(md_dir):
        section_files = [f for f in os.listdir(md_dir) if f.startswith("ODD_Section_") and f.endswith(".md")]
    
    if not section_files:
        st.warning(f"No section files found in {md_dir}. Please check the directory path.")
        return
    
    # Sort section files numerically
    section_files.sort(key=lambda x: int(re.search(r'Section_(\d+)', x).group(1)))
    
    # Select section
    selected_section = st.sidebar.selectbox(
        "Select Section", 
        section_files,
        format_func=lambda x: f"Section {re.search(r'Section_(\d+)', x).group(1)}"
    )
    
    if not selected_section:
        st.info("Please select a section to view.")
        return
    
    section_num = re.search(r'Section_(\d+)', selected_section).group(1)
    
    # Paths
    md_path = os.path.join(md_dir, selected_section)
    yaml_path = os.path.join(yaml_dir, f"odd{section_num}.yaml")
    results_path = os.path.join(results_dir, f"Section{section_num}_eval.csv")
    
    # Load data
    md_content = load_markdown_file(md_path)
    yaml_requirements = load_yaml_requirements(yaml_path)
    results_df = load_evaluation_results(results_path)
    
    # Main content
    st.header(f"Section {section_num}")
    
    # Create tabs for different views
    section_tabs = st.tabs(["Content", "Requirements", "Evaluation Results"])
    
    # Content tab
    with section_tabs[0]:
        st.markdown("### Markdown Content")
        st.markdown(md_content)
    
    # Requirements tab
    with section_tabs[1]:
        st.markdown("### Requirements")
        if yaml_requirements:
            for item in yaml_requirements:
                st.markdown(f"#### {item.get('section', 'No title')}")
                st.markdown(item.get('prompt', 'No requirements'))
                st.divider()
        else:
            st.info("No requirements found.")
    
    # Evaluation Results tab
    with section_tabs[2]:
        st.markdown("### Evaluation Results")
        if results_df is not None and not results_df.empty:
            # For each section in the results
            for idx, row in results_df.iterrows():
                section_title = row['Section Title']
                
                st.markdown(f"#### {section_title}")
                st.markdown("**Content:**")
                st.markdown(row['Content'])
                
                st.markdown("**Requirements:**")
                st.markdown(row['Requirements'])
                
                st.markdown("**Evaluation Metrics:**")
                
                # Create a 2x2 grid for the metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    # Coherence
                    coherence_score = row['Coherence Score']
                    coherence_comment = row['Coherence Comment']
                    coherence_color = map_score_to_color(coherence_score)
                    display_metric_card("Coherence", coherence_score, coherence_comment, coherence_color)
                    
                    # Quality
                    quality_score = row['Quality Score']
                    quality_comment = row['Quality Comment']
                    quality_color = map_score_to_color(quality_score)
                    display_metric_card("Quality", quality_score, quality_comment, quality_color)
                
                with col2:
                    # Capture Rate
                    capture_score = row['Capture Rate']
                    capture_comment = row['Capture Comment']
                    capture_color = map_score_to_color(capture_score)
                    display_metric_card("Capture Rate", capture_score, capture_comment, capture_color)
                    
                    # Hallucination - Note: Lower is better for hallucination
                    hallucination_score = row['Hallucination Score']
                    hallucination_comment = row['Hallucination Comment']
                    hallucination_color = map_score_to_color(hallucination_score, inverted=True)
                    display_metric_card("Hallucination", hallucination_score, hallucination_comment, hallucination_color)
                
                # Overall score
                average_score = row['Average Score']
                avg_color = map_score_to_color(average_score)
                st.markdown(f"""
                <div style="border:1px solid {avg_color}; border-radius:5px; padding:10px; margin:10px 0; text-align:center;">
                    <h3>Overall Score: <span style="color:{avg_color};">{average_score:.2f}</span></h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.divider()
        else:
            st.warning(f"No evaluation results found at {results_path}")
            st.info("Run the evaluation tool first or check the results directory path.")

def main():
    """Main function to run the Streamlit app."""
    
    st.title("Documentation Evaluation Dashboard")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    yaml_dir = st.sidebar.text_input("YAML Directory", DEFAULT_YAML_DIR)
    md_dir = st.sidebar.text_input("Markdown Directory", DEFAULT_MD_DIR)
    results_dir = st.sidebar.text_input("Results Directory", DEFAULT_RESULTS_DIR)
    
    # Sidebar navigation
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Select View", ["Dashboard", "Section Details"])

    # Show either Dashboard or Section Details based on navigation
    if page == "Dashboard":
        # Display dashboard with visualizations
        display_dashboard(results_dir)
    else:  # Section Details
        show_section_details(yaml_dir, md_dir, results_dir)

if __name__ == "__main__":
    main()