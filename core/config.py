"""
Configuration management for documentation evaluation.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AppConfig:
    """Application configuration manager."""
    
    DEFAULT_CONFIG = {
        'yaml_dir': './config',
        'md_dir': './examples',
        'output_dir': './evaluation_results',
        'prompt_file': './config/prompts.yaml',
        'section_range': (1, 6),
        'model_params': {
            'temperature': 0.0,
            'max_workers': 4
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to a YAML config file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to YAML config file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                
            if yaml_config and isinstance(yaml_config, dict):
                # Update config with loaded values
                self._update_config(yaml_config)
                logger.info(f"Configuration loaded from {file_path}")
                return True
            else:
                logger.warning(f"Invalid configuration in {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading config from {file_path}: {e}")
            return False
    
    def _update_config(self, new_values: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            new_values: Dictionary with new configuration values
        """
        # Update top-level values
        for key, value in new_values.items():
            if key == 'model_params' and isinstance(value, dict):
                # Merge model_params dictionary
                if 'model_params' not in self.config:
                    self.config['model_params'] = {}
                self.config['model_params'].update(value)
            elif key == 'section_range' and isinstance(value, str):
                # Convert section range string to tuple
                self.config['section_range'] = self._parse_section_range(value)
            else:
                self.config[key] = value
    
    def _parse_section_range(self, range_str: str) -> tuple:
        """
        Parse section range string to tuple.
        
        Args:
            range_str: Range string like "1-5" or "3"
            
        Returns:
            Tuple of (start, end+1)
        """
        try:
            if '-' in range_str:
                start, end = map(int, range_str.split('-'))
                return (start, end + 1)  # End is inclusive
            else:
                # Single section
                section = int(range_str)
                return (section, section + 1)
        except ValueError:
            logger.warning(f"Invalid section range: {range_str}. Using default.")
            return self.DEFAULT_CONFIG['section_range']
    
    def update_from_args(self, args_dict: Dict[str, Any]) -> None:
        """
        Update configuration from command line arguments.
        
        Args:
            args_dict: Dictionary with argument values
        """
        # Process different arg formats
        model_params = {}
        
        # Extract model params from args
        if 'model' in args_dict and args_dict['model']:
            model_params['model'] = args_dict['model']
        
        if 'temperature' in args_dict:
            model_params['temperature'] = args_dict['temperature']
            
        if 'max_workers' in args_dict:
            model_params['max_workers'] = args_dict['max_workers']
        
        # Update main config items (only if they have values)
        update_dict = {}
        for key in ['yaml_dir', 'md_dir', 'output_dir', 'prompt_file']:
            if key in args_dict and args_dict[key]:
                update_dict[key] = args_dict[key]
        
        # Handle section range
        if 'section_range' in args_dict and args_dict['section_range']:
            update_dict['section_range'] = self._parse_section_range(args_dict['section_range'])
        
        # Update model params
        if model_params:
            update_dict['model_params'] = model_params
        
        # Apply updates
        self._update_config(update_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access to configuration."""
        return self.config[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in configuration."""
        return key in self.config