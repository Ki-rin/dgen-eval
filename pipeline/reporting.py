# pipeline/reporting.py
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from core.data_models import EvaluationReport

def create_csv_report(reports: List[EvaluationReport], output_file: str) -> None:
    """
    Create a CSV report from evaluation results.
    
    Args:
        reports: List of evaluation reports
        output_file: Path to save CSV file
    """
    rows = []
    
    for report in reports:
        row = {
            'Section ID': report.section.section_id,
            'Section Title': report.section.title,
            'Content': report.section.content,
            'Requirements': '\n'.join(report.section.requirements) if report.section.requirements else '',
            'Coherence Score': report.metrics.get('coherence', {}).score if 'coherence' in report.metrics else '',
            'Quality Score': report.metrics.get('quality', {}).score if 'quality' in report.metrics else '',
            'Capture Rate': report.metrics.get('capture', {}).score if 'capture' in report.metrics else '',
            'Hallucination Score': report.metrics.get('hallucination', {}).score if 'hallucination' in report.metrics else '',
            'Coherence Comment': report.metrics.get('coherence', {}).comment if 'coherence' in report.metrics else '',
            'Quality Comment': report.metrics.get('quality', {}).comment if 'quality' in report.metrics else '',
            'Capture Comment': report.metrics.get('capture', {}).comment if 'capture' in report.metrics else '',
            'Hallucination Comment': report.metrics.get('hallucination', {}).comment if 'hallucination' in report.metrics else '',
            'Average Score': report.average_score()
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Report saved to {output_file}")

def merge_csv_reports(report_files: List[str], output_file: str) -> None:
    """
    Merge multiple CSV reports into a single file.
    
    Args:
        report_files: List of CSV report file paths
        output_file: Path for merged output file
    """
    dfs = []
    
    for file_path in report_files:
        try:
            df = pd.read_csv(file_path)
            # Add file name as a column
            df['Source'] = os.path.basename(file_path)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        merged_df.to_csv(output_file, index=False)
        print(f"Merged report saved to {output_file}")
    else:
        print("No valid reports to merge")