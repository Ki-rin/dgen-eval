#!/usr/bin/env python3
"""
Setup script for Documentation Evaluation Dashboard
"""

import os
import re
from setuptools import setup, find_packages

# Get the version from the package
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "doc_evaluator", "__init__.py")
    if not os.path.exists(init_path):
        # Create a minimal __init__.py if it doesn't exist
        os.makedirs(os.path.dirname(init_path), exist_ok=True)
        with open(init_path, "w") as f:
            f.write('"""Documentation Evaluation Dashboard"""\n\n__version__ = "0.1.0"\n')
    
    with open(init_path) as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
    return "0.1.0"  # Default version if not found

# Read long description from README
def get_long_description():
    with open("README.md", encoding="utf-8") as f:
        return f.read()

# Get requirements
def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

# Define entry points
entry_points = {
    'console_scripts': [
        'doc-evaluator-cli=doc_evaluator.cli:main',
        'doc-evaluator-dashboard=doc_evaluator.app:main',
        'doc-evaluator-init=doc_evaluator.init_eval_environment:main',
    ],
}

# Define package data
package_data = {
    'doc_evaluator': [
        'config/*.yaml',
        'examples/*.md',
    ],
}

setup(
    name="doc-evaluator",
    version=get_version(),
    description="Modular Documentation Evaluation Dashboard",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Your Organization",
    author_email="your.email@example.com",
    url="https://github.com/your-org/doc-evaluator",
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    install_requires=get_requirements(),
    entry_points=entry_points,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    keywords="documentation, evaluation, dashboard, nlp, llm",
    project_urls={
        "Documentation": "https://github.com/your-org/doc-evaluator",
        "Source": "https://github.com/your-org/doc-evaluator",
        "Tracker": "https://github.com/your-org/doc-evaluator/issues",
    },
)