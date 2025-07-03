#!/usr/bin/env python3
"""
MRM Documentation Cleaner v2

Enhanced script to clean MRM (Model Risk Management) documentation by removing
unnecessary adjectives, correcting contradictions, and ensuring accuracy for
RAG/API-based models rather than training-focused implementations.

v2 Changes:
- Only processes .json and .md files (no copying of other files)
- Maintains original formatting without adding markdown code blocks
- Improved prompt engineering for format preservation
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


class MRMDocumentationCleanerV2:
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
        """Generate cleaning prompt based on file type with strict formatting preservation."""
        if file_path.suffix.lower() == '.md':
            return f"""
You are cleaning MRM (Model Risk Management) documentation for models using RAG, API calls, or pre-trained models (NOT custom training).

Clean this Markdown document by:
1. REMOVE unnecessary adjectives ("comprehensive", "robust", "innovative", etc.)
2. REMOVE non-informative phrases ("it should be noted", "importantly", etc.)
3. FIX contradictory statements about model approaches
4. REPLACE training language with RAG/API language where appropriate
5. MAKE statements direct and factual
6. REMOVE redundant information
7. KEEP technical accuracy and MRM compliance

CRITICAL FORMATTING REQUIREMENTS:
- PRESERVE the exact markdown structure (headers, lists, tables, etc.)
- MAINTAIN original spacing and indentation
- KEEP the same heading levels (# ## ### etc.)
- PRESERVE bullet points and numbering exactly as they are
- DO NOT add markdown code blocks or backticks around the response
- DO NOT change the document structure or organization
- Return ONLY the cleaned markdown content, no additional formatting

Original document:
{content}

Return the cleaned markdown maintaining identical structure:"""
        
        elif file_path.suffix.lower() == '.json':
            return f"""
Clean this MRM JSON configuration for RAG/API-based models:

1. REMOVE redundant fields
2. FIX contradictory values  
3. REMOVE training-specific parameters
4. ENSURE RAG/API accuracy
5. FIX naming inconsistencies
6. KEEP MRM compliance fields

CRITICAL FORMATTING REQUIREMENTS:
- PRESERVE exact JSON structure and indentation
- MAINTAIN original key ordering where possible
- KEEP valid JSON syntax
- DO NOT add markdown code blocks or backticks
- Return ONLY the cleaned JSON content

Original JSON:
{content}

Return the cleaned JSON maintaining identical structure:"""
        
        else:
            return f"""
Clean this MRM documentation by removing fluff and fixing contradictions.

PRESERVE the original formatting exactly. DO NOT add markdown code blocks.

Original:
{content}

Return cleaned content with identical formatting:"""
    
    def clean_file_content(self, file_path: Path, content: str) -> str:
        """Clean content using LLM with format preservation and empty file retry."""
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
                    
                    # Post-process to ensure no markdown code blocks were added
                    cleaned = self.remove_unwanted_formatting(cleaned, file_path)
                    
                    # Check if result is empty or too short
                    if not cleaned or len(cleaned.strip()) < 10:
                        logger.warning(f"Empty/short result for {file_path.name}, attempt {attempt + 1}")
                        if attempt < 2:
                            # Retry with slightly different prompt
                            time.sleep(1)
                            continue
                        else:
                            # Return original if all attempts produce empty results
                            logger.error(f"All attempts produced empty results for {file_path.name}, returning original")
                            return content
                    
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
    
    def remove_unwanted_formatting(self, content: str, file_path: Path) -> str:
        """Remove any unwanted markdown code blocks or formatting added by LLM."""
        # Remove markdown code blocks if they were added
        if file_path.suffix.lower() == '.md':
            # Remove ```markdown and ``` if present
            content = content.replace('```markdown\n', '').replace('```markdown', '')
            content = content.replace('\n```', '').replace('```', '')
        elif file_path.suffix.lower() == '.json':
            # Remove ```json and ``` if present
            content = content.replace('```json\n', '').replace('```json', '')
            content = content.replace('\n```', '').replace('```', '')
        
        # Remove any leading/trailing whitespace but preserve internal structure
        content = content.strip()
        
        return content
    
    def should_process_file(self, file_path: Path) -> bool:
        """Only process .json and .md files."""
        return (not file_path.name.startswith('.') and 
                file_path.suffix.lower() in {'.md', '.json'})
    
    def clean_target_files(self) -> Dict[str, int]:
        """Clean only .json and .md files, ignore all others."""
        stats = {'cleaned': 0, 'skipped': 0, 'errors': 0, 'empty_retries': 0}
        
        # Get only .json and .md files
        target_files = []
        for pattern in ['**/*.md', '**/*.json']:
            target_files.extend(self.source_dir.glob(pattern))
        
        # Remove hidden files
        target_files = [f for f in target_files if not f.name.startswith('.')]
        
        logger.info(f"Found {len(target_files)} target files (.md/.json)")
        
        for source_file in target_files:
            try:
                relative_path = source_file.relative_to(self.source_dir)
                target_file = self.target_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Clean the file
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Skip if original file is empty
                    if not content or len(content.strip()) < 5:
                        logger.warning(f"Original file {source_file.name} is empty or too short, skipping")
                        stats['skipped'] += 1
                        continue
                    
                    cleaned_content = self.clean_file_content(source_file, content)
                    
                    # Final check: if cleaned content is empty, use original
                    if not cleaned_content or len(cleaned_content.strip()) < 10:
                        logger.warning(f"Cleaned content for {source_file.name} is empty, using original")
                        cleaned_content = content
                        stats['empty_retries'] += 1
                    
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    stats['cleaned'] += 1
                    
                except UnicodeDecodeError:
                    logger.warning(f"Encoding issue with {source_file}, skipping")
                    stats['skipped'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {source_file}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def run(self) -> Dict[str, int]:
        """Run the complete cleaning process."""
        logger.info("Starting MRM documentation cleaning (v2)...")
        start_time = time.time()
        
        stats = self.clean_target_files()
        
        end_time = time.time()
        logger.info("=" * 50)
        logger.info("CLEANING COMPLETE (v2)")
        logger.info("=" * 50)
        logger.info(f"Files cleaned: {stats['cleaned']}")
        logger.info(f"Files skipped: {stats['skipped']}")
        logger.info(f"Empty retries: {stats['empty_retries']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info(f"Time taken: {end_time - start_time:.2f} seconds")
        logger.info(f"Results in: {self.target_dir}")
        
        return stats


# Simple functions to run from code
def clean_mrm_docs_v2(source_dir: str, target_dir: str, temperature: float = 0.05) -> Dict[str, int]:
    """
    Clean MRM documentation with v2 settings (only .md and .json files).
    
    Args:
        source_dir: Path to original MRM docs
        target_dir: Path for cleaned docs  
        temperature: LLM temperature (default: 0.05 for consistency)
    
    Returns:
        Stats dict with 'cleaned', 'skipped', 'errors', 'empty_retries' counts
    
    Example:
        stats = clean_mrm_docs_v2("./docs", "./docs_cleaned")
        print(f"Cleaned {stats['cleaned']} files")
    """
    cleaner = MRMDocumentationCleanerV2(source_dir, target_dir, temperature)
    return cleaner.run()


def quick_clean_v2(source_dir: str, target_dir: str = None) -> None:
    """
    Simplest way to clean MRM docs v2 - only .md and .json files.
    
    Args:
        source_dir: Directory with MRM docs to clean
        target_dir: Optional target (defaults to source_dir + "_cleaned_v2")
    
    Example:
        quick_clean_v2("./my_mrm_docs")
        # Creates ./my_mrm_docs_cleaned_v2/
    """
    if target_dir is None:
        target_dir = f"{source_dir.rstrip('/')}_cleaned_v2"
    
    print(f"Cleaning MRM docs v2: {source_dir} -> {target_dir}")
    stats = clean_mrm_docs_v2(source_dir, target_dir)
    
    print("\n" + "="*40)
    print("🧹 MRM DOCS CLEANED! (v2)")
    print("="*40)
    print(f"✅ Cleaned: {stats['cleaned']} files (.json/.md only)")
    print(f"⏭️  Skipped: {stats['skipped']} files (encoding issues)")
    print(f"🔄 Empty retries: {stats['empty_retries']} files (used original)")
    print(f"❌ Errors: {stats['errors']} files")
    print(f"📂 Output: {target_dir}")
    print(f"📝 Note: Only .md and .json files processed")


# Example usage
if __name__ == "__main__":
    
    # Comprehensive example showing all features
    print("🧹 MRM Documentation Cleaner v2 - Full Example")
    print("=" * 50)
    
    # Clean MRM docs with all features
    source_directory = "./mrm_documentation"
    target_directory = "./mrm_documentation_cleaned"
    
    print(f"📁 Source: {source_directory}")
    print(f"📁 Target: {target_directory}")
    print("🔧 Processing only .md and .json files")
    print("🔄 Auto-retry for empty results")
    print("📐 Preserving original formatting")
    
    # Run the cleaning
    stats = clean_mrm_docs_v2(
        source_dir=source_directory,
        target_dir=target_directory,
        temperature=0.05  # Low temperature for consistency
    )
    
    # Final summary
    print("\n🎉 Processing Complete!")
    print(f"✅ Successfully cleaned: {stats['cleaned']} files")
    print(f"⏭️  Skipped (encoding/empty): {stats['skipped']} files") 
    print(f"🔄 Used original (empty retry): {stats['empty_retries']} files")
    print(f"❌ Errors: {stats['errors']} files")
    print(f"📂 Results saved to: {target_directory}")
    
    # Alternative: Quick clean with auto-generated target
    print("\n" + "="*50)
    print("🚀 Quick Clean Alternative:")
    print("quick_clean_v2('./my_docs')  # Creates ./my_docs_cleaned_v2/")
    
    print("\n✨ Done!")
