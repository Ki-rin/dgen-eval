# pipeline/document_processors.py
import yaml
import re
import os
from typing import List, Dict, Any, Optional
from core.data_models import DocumentSection
from llm.adapter import call_llm

def extract_sections(yaml_file: str, md_file: str) -> List[DocumentSection]:
    """
    Extract document sections from YAML questions and markdown content.
    
    Args:
        yaml_file: Path to YAML file with questions
        md_file: Path to markdown file with content
        
    Returns:
        List of DocumentSection objects
    """
    # Load YAML questions
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Load markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract sections from markdown
    section_pattern = r'## (.+?)\n(.*?)(?=\n## |\Z)'
    matches = re.finditer(section_pattern, md_content, re.DOTALL)
    
    section_content = {}
    for match in matches:
        section_title = match.group(1).strip()
        content = match.group(2).strip()
        section_content[section_title] = content
    
    # Create DocumentSection objects
    sections = []
    for item in yaml_data:
        section_title = item.get('section', '')
        prompt = item.get('prompt', '')
        
        section_id = f"section_{len(sections) + 1}"
        
        content = ""
        # Try to find matching content
        if section_title in section_content:
            content = section_content[section_title]
        else:
            # Try fuzzy matching
            for md_title, md_content in section_content.items():
                if section_title in md_title or md_title in section_title:
                    content = md_content
                    break
        
        if content:
            sections.append(DocumentSection(
                section_id=section_id,
                title=section_title,
                content=content,
                requirements=[prompt] if prompt else None
            ))
    
    return sections

def generate_requirements(section: DocumentSection, model_params: Optional[Dict[str, Any]] = None) -> DocumentSection:
    """
    Generate requirements for a document section using LLM.
    
    Args:
        section: Document section to generate requirements for
        model_params: Optional parameters for LLM call
        
    Returns:
        Updated DocumentSection with requirements
    """
    model_params = model_params or {}
    
    prompt = f"""
    Generate specific requirements for documentation about:
    
    Title: {section.title}
    
    The documentation should be evaluated on:
    - Coherence and clarity
    - Completeness of information
    - Relevance to the topic
    - Absence of fabricated information
    
    List 3-5 specific requirements that should be met, separated by newlines.
    """
    
    response = call_llm(prompt=prompt, **model_params)
    
    # Parse requirements from response
    from llm.parsers import extract_requirements_from_llm
    requirements = extract_requirements_from_llm(response)
    
    # Create updated section
    return DocumentSection(
        section_id=section.section_id,
        title=section.title,
        content=section.content,
        requirements=requirements
    )
