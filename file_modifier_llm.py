#!/usr/bin/env python3
"""
MRM Documentation Cleaner

Simple script to clean MRM (Model Risk Management) documentation by removing
unnecessary adjectives, correcting contradictions, and ensuring accuracy for
RAG/API-based models rather than training-focused implementations.

Only processes .json and .md files.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, Callable
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import the LLM connector
try:
    from dgen_llm.llm_connector import generate_content as dgen_generate_content
    HAS_DGEN_LLM = True
    logger.info("dgen_llm module found and imported successfully")
except ImportError:
    HAS_DGEN_LLM = False
    logger.warning("dgen_llm module not found. Using mock implementation.")
    
    def dgen_generate_content(prompt: str, **kwargs) -> str:
        """Mock LLM implementation for testing."""
        content = kwargs.get('content', '')
        return f"# Cleaned by LLM\n{content}\n# End of LLM cleaning"


class MRMDocumentationCleaner:
    """Clean MRM documentation using LLM to remove fluff and fix contradictions."""
    
    def __init__(self, source_dir: str, target_dir: str, temperature: float = 0.05):
        """
        Initialize the cleaner.
        
        Args:
            source_dir: Source directory with MRM docs
            target_dir: Target directory for cleaned docs
            temperature: LLM temperature (0.05 for consistent output)
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.temperature = temperature
        
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        self.target_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Will clean docs from {self.source_dir} to {self.target_dir}")
    
    def get_cleaning_prompt(self, file_path: Path, content: str) -> str:
        """Generate cleaning prompt based on file type."""
        if file_path.suffix.lower() == '.md':
            return f"""
You are cleaning MRM (Model Risk Management) documentation for models using RAG, API calls, or pre-trained models (NOT custom training).

Clean this Markdown by:
1. REMOVE unnecessary adjectives ("comprehensive", "robust", "innovative", etc.)
2. REMOVE non-informative phrases ("it should be noted", "importantly", etc.)
3. FIX contradictory statements about model approaches
4. REPLACE training language with RAG/API language where appropriate
5. MAKE statements direct and factual
6. REMOVE redundant information
7. KEEP technical accuracy and MRM compliance

Original:
{content}

Return only the cleaned markdown content. Do NOT wrap your response in markdown code blocks (```markdown). Return the raw markdown content directly.
"""
        elif file_path.suffix.lower() == '.json':
            return f"""
Clean this MRM JSON configuration for RAG/API-based models:

1. REMOVE redundant fields
2. FIX contradictory values  
3. REMOVE training-specific parameters
4. ENSURE RAG/API accuracy
5. FIX naming inconsistencies
6. KEEP MRM compliance fields

Original:
{content}

Return only the cleaned JSON content. Do NOT wrap your response in code blocks (```json). Return the raw JSON content directly.
"""
        else:
            return f"Clean this MRM documentation by removing fluff and fixing contradictions. Do NOT wrap your response in code blocks. Return the raw content directly:\n{content}"
    
    def remove_markdown_wrapper(self, content: str, file_path: Path) -> str:
        """Remove markdown code block wrappers from LLM output."""
        content = content.strip()
        
        # Remove markdown code block wrappers
        if content.startswith('```'):
            lines = content.split('\n')
            
            # Remove opening wrapper (```markdown, ```json, ```md, etc.)
            if lines[0].startswith('```'):
                lines = lines[1:]
            
            # Remove closing wrapper
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            
            content = '\n'.join(lines)
            logger.debug(f"Removed markdown wrapper from {file_path.name}")
        
        return content.strip()

    def clean_file_content(self, file_path: Path, content: str) -> str:
        """Clean content using LLM."""
        try:
            prompt = self.get_cleaning_prompt(file_path, content)
            
            # Try LLM call with retries
            for attempt in range(3):
                try:
                    cleaned = dgen_generate_content(
                        prompt=prompt,
                        content=content,
                        temperature=self.temperature
                    )
                    
                    # Remove markdown wrappers before saving
                    cleaned = self.remove_markdown_wrapper(cleaned, file_path)
                    
                    logger.info(f"Cleaned: {file_path.name}")
                    return cleaned
                except Exception as e:
                    if attempt < 2:
                        logger.warning(f"Retry {attempt + 1} for {file_path.name}: {e}")
                        time.sleep(1)
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Failed to clean {file_path.name}: {e}")
            return f"# Error during cleaning: {str(e)}\n# Original content:\n{content}"
    
    def should_process_file(self, file_path: Path) -> bool:
        """Only process .json and .md files."""
        return (not file_path.name.startswith('.') and 
                file_path.suffix.lower() in {'.md', '.json'})
    
    def copy_other_files(self, source_file: Path, target_file: Path):
        """Copy non-.json/.md files without changes."""
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)
        logger.info(f"Copied: {source_file.name}")
    
    def clean_all_files(self) -> Dict[str, int]:
        """Clean all MRM documentation files."""
        stats = {'cleaned': 0, 'copied': 0, 'errors': 0}
        
        # Get all files
        all_files = [f for f in self.source_dir.rglob('*') if f.is_file()]
        logger.info(f"Found {len(all_files)} total files")
        
        for source_file in all_files:
            try:
                relative_path = source_file.relative_to(self.source_dir)
                target_file = self.target_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                if self.should_process_file(source_file):
                    # Clean .json and .md files
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        cleaned_content = self.clean_file_content(source_file, content)
                        
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(cleaned_content)
                        
                        stats['cleaned'] += 1
                        
                    except UnicodeDecodeError:
                        # Handle encoding issues
                        self.copy_other_files(source_file, target_file)
                        stats['copied'] += 1
                else:
                    # Copy other files unchanged
                    self.copy_other_files(source_file, target_file)
                    stats['copied'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {source_file}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def run(self) -> Dict[str, int]:
        """Run the complete cleaning process."""
        logger.info("Starting MRM documentation cleaning...")
        start_time = time.time()
        
        stats = self.clean_all_files()
        
        end_time = time.time()
        logger.info("=" * 50)
        logger.info("CLEANING COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Files cleaned: {stats['cleaned']}")
        logger.info(f"Files copied: {stats['copied']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Time taken: {end_time - start_time:.2f} seconds")
        logger.info(f"Results in: {self.target_dir}")
        
        return stats


# Simple functions to run from code
def clean_mrm_docs(source_dir: str, target_dir: str, temperature: float = 0.05) -> Dict[str, int]:
    """
    Clean MRM documentation with default settings.
    
    Args:
        source_dir: Path to original MRM docs
        target_dir: Path for cleaned docs  
        temperature: LLM temperature (default: 0.05 for consistency)
    
    Returns:
        Stats dict with 'cleaned', 'copied', 'errors' counts
    
    Example:
        stats = clean_mrm_docs("./docs", "./docs_cleaned")
        print(f"Cleaned {stats['cleaned']} files")
    """
    cleaner = MRMDocumentationCleaner(source_dir, target_dir, temperature)
    return cleaner.run()


def quick_clean(source_dir: str, target_dir: str = None) -> None:
    """
    Simplest way to clean MRM docs - just specify source directory.
    
    Args:
        source_dir: Directory with MRM docs to clean
        target_dir: Optional target (defaults to source_dir + "_cleaned")
    
    Example:
        quick_clean("./my_mrm_docs")
        # Creates ./my_mrm_docs_cleaned/
    """
    if target_dir is None:
        target_dir = f"{source_dir.rstrip('/')}_cleaned"
    
    print(f"Cleaning MRM docs: {source_dir} -> {target_dir}")
    stats = clean_mrm_docs(source_dir, target_dir)
    
    print("\n" + "="*40)
    print("🧹 MRM DOCS CLEANED!")
    print("="*40)
    print(f"✅ Cleaned: {stats['cleaned']} files (.json/.md)")
    print(f"📁 Copied: {stats['copied']} files (other types)")
    print(f"❌ Errors: {stats['errors']} files")
    print(f"📂 Output: {target_dir}")


# Examples for running from main
if __name__ == "__main__":
    
    # Example 1: Quick clean with auto-generated target directory
    print("Example 1: Quick clean")
    quick_clean("./examples")  # Creates ./examples_cleaned/
    
    # Example 2: Specify both directories
    print("\nExample 2: Custom directories")
    stats = clean_mrm_docs(
        source_dir="./config", 
        target_dir="./config_cleaned"
    )
    print(f"Processed {stats['cleaned'] + stats['copied']} files")
    
    # Example 3: Higher temperature for more creative cleaning
    print("\nExample 3: Higher temperature")
    clean_mrm_docs(
        source_dir="./examples",
        target_dir="./examples_creative", 
        temperature=0.2
    )
    
    # Example 4: Using the class directly
    print("\nExample 4: Direct class usage")
    cleaner = MRMDocumentationCleaner(
        source_dir="./evaluation_results",
        target_dir="./evaluation_results_cleaned",
        temperature=0.05
    )
    cleaner.run()
    
    print("\n🎉 All examples completed!")
