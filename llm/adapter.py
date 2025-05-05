# llm/adapter.py
import time
import random
import logging
from typing import List, Dict, Any, Optional, Callable
import concurrent.futures

logger = logging.getLogger(__name__)

# Try to import the actual LLM connector
try:
    from dgen_llm.llm_connector import generate_content as dgen_generate_content
    HAS_DGEN_LLM = True
except ImportError:
    HAS_DGEN_LLM = False
    logger.warning("dgen_llm module not found. Using mock implementation.")
    
    def dgen_generate_content(prompt: str, **kwargs) -> str:
        """Mock LLM implementation."""
        return f"Score: 0.75\nThis content shows reasonable coherence and quality."

def call_llm(prompt: str, **kwargs) -> str:
    """
    Call LLM with retry logic and error handling.
    
    Args:
        prompt: The prompt to send to the LLM
        **kwargs: Additional parameters for the LLM
            - retry_count: Number of retries (default: 3)
            - retry_delay: Base delay between retries (default: 1.0)
            
    Returns:
        Generated text from the LLM
    """
    retry_count = kwargs.pop('retry_count', 3)
    retry_delay = kwargs.pop('retry_delay', 1.0)
    
    for attempt in range(retry_count + 1):
        try:
            if HAS_DGEN_LLM:
                return dgen_generate_content(prompt=prompt, **kwargs)
            else:
                return dgen_generate_content(prompt=prompt, **kwargs)
        except Exception as e:
            if attempt < retry_count:
                sleep_time = retry_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"LLM call failed (attempt {attempt+1}/{retry_count+1}): {e}. Retrying in {sleep_time:.2f}s")
                time.sleep(sleep_time)
            else:
                logger.error(f"LLM call failed after {retry_count+1} attempts: {e}")
                return f"Error calling LLM: {str(e)}"

def batch_process_texts(prompts: List[str], max_workers: int = 4, **kwargs) -> List[str]:
    """
    Process multiple prompts in parallel.
    
    Args:
        prompts: List of prompts to process
        max_workers: Maximum number of parallel workers
        **kwargs: Additional parameters for call_llm
        
    Returns:
        List of LLM responses in the same order as prompts
    """
    results = [None] * len(prompts)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(call_llm, prompt=prompt, **kwargs): i
            for i, prompt in enumerate(prompts)
        }
        
        for future in concurrent.futures.as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
                results[idx] = f"Error: {str(e)}"
    
    return results