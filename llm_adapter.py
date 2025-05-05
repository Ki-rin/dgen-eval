"""
Simple adapter for LLM integration
This module provides a thin adapter layer to call llm.
"""

import concurrent.futures
from typing import List

try:
    from dgen_llm.llm_connector import generate_content
except ImportError:
    def generate_content(prompt: str, **kwargs) -> str:
        """Fallback: echo the first 20 characters of the prompt, with handling for empty or short input."""
        stripped = prompt.strip()
        if not stripped:
            return "LLM Mock Echo: [empty prompt]"
        if len(stripped) < 20:
            return f"LLM Mock Echo: [short prompt] {stripped}"
        return f"LLM Mock Echo: {stripped[:20]}"


def call_llm(prompt: str, **kwargs) -> str:
    """
    Call LLM with the given prompt.

    Args:
        prompt: Prompt text to send to the LLM
        **kwargs: Additional keyword arguments for generate_content

    Returns:
        Generated text from the LLM, or a fallback echo
    """
    try:
        return generate_content(prompt=prompt, **kwargs)
    except Exception as e:
        return f"Error calling LLM: {str(e)}"

def batch_process_texts_parallel(prompts: List[str], max_workers: int = 4, **kwargs) -> List[str]:
    """
    Process multiple prompts in parallel.

    Args:
        prompts: List of prompt strings
        max_workers: Number of parallel workers
        **kwargs: Additional keyword arguments passed to call_llm

    Returns:
        List of LLM-generated responses, preserving input order
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
                results[idx] = f"Error: {str(e)}"
    return results

def batch_process_texts(prompts: List[str], parallel: bool = True, max_workers: int = 4, **kwargs) -> List[str]:
    """
    Process multiple prompts (in parallel or sequentially).

    Args:
        prompts: List of prompts to process
        parallel: Whether to run processing in parallel
        max_workers: Number of workers if parallel
        **kwargs: Additional keyword arguments for call_llm

    Returns:
        List of LLM-generated responses
    """
    if parallel:
        return batch_process_texts_parallel(prompts, max_workers=max_workers, **kwargs)
    return [call_llm(prompt=prompt, **kwargs) for prompt in prompts]

def process_with_template(texts: List[str], template: str, parallel: bool = True, max_workers: int = 4, **kwargs) -> List[str]:
    """
    Format input texts using a template and process via LLM.

    Args:
        texts: List of raw input strings
        template: Template string with `{text}` placeholder
        parallel: Whether to run in parallel
        max_workers: Number of parallel workers
        **kwargs: Additional keyword arguments for call_llm

    Returns:
        List of generated responses for templated prompts
    """
    prompts = [template.format(text=text) for text in texts]
    return batch_process_texts(prompts=prompts, parallel=parallel, max_workers=max_workers, **kwargs)