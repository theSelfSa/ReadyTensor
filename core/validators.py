"""
Logic-based validation - exact port from original config/logic_based_scoring.py
Preserve all validation functions and decorator patterns
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Callable, List
import logging

logger = logging.getLogger(__name__)

# Preserve original decorator pattern
def scoring_function(func: Callable) -> Callable:
    """Decorator for scoring functions - exact copy from original"""
    func.is_scoring_function = True
    return func

class LogicBasedValidator:
    """Logic-based validation - port all functions from original logic_based_scoring.py"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def assess_repository(self, repo_path: str) -> Dict[str, Any]:
        """Run all logic-based assessments"""
        results = {}
        
        # Get all scoring functions (same pattern as original)
        scoring_methods = [getattr(self, method) for method in dir(self) 
                          if hasattr(getattr(self, method), 'is_scoring_function')]
        
        for method in scoring_methods:
            try:
                criterion_id = method.__name__
                logger.info(f"Scoring criterion: {criterion_id}")
                result = method(repo_path)
                results[criterion_id] = result
            except Exception as e:
                logger.error(f"Error scoring {method.__name__}: {e}")
                results[method.__name__] = {"score": 0, "error": str(e)}
        
        return results
    
    @scoring_function
    def readme_presence(self, repo_path: str) -> Dict[str, Any]:
        """Check for README file - exact copy from original"""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        
        for readme_file in readme_files:
            if os.path.exists(os.path.join(repo_path, readme_file)):
                return {
                    "score": 100,
                    "explanation": f"Found {readme_file}",
                    "evidence": readme_file
                }
        
        return {
            "score": 0,
            "explanation": "No README file found",
            "evidence": None
        }
    
    @scoring_function
    def license_presence(self, repo_path: str) -> Dict[str, Any]:
        """Check for license file - exact copy from original"""
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENCE']
        
        for license_file in license_files:
            if os.path.exists(os.path.join(repo_path, license_file)):
                return {
                    "score": 100,
                    "explanation": f"Found {license_file}",
                    "evidence": license_file
                }
        
        return {
            "score": 0,
            "explanation": "No license file found",
            "evidence": None
        }
    
    @scoring_function
    def script_length(self, repo_path: str) -> Dict[str, Any]:
        """Check script lengths - exact copy from original"""
        python_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        long_files = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = len(f.readlines())
                    if line_count > 500:  # Same threshold as original
                        long_files.append((file_path, line_count))
            except Exception:
                continue
        
        if not long_files:
            return {
                "score": 100,
                "explanation": "All Python files are reasonably sized",
                "evidence": f"Checked {len(python_files)} files"
            }
        
        return {
            "score": max(0, 100 - len(long_files) * 20),
            "explanation": f"Found {len(long_files)} files exceeding 500 lines",
            "evidence": long_files
        }
    
    @scoring_function
    def repository_size(self, repo_path: str) -> Dict[str, Any]:
        """Check repository size - exact copy from original"""
        total_size = 0
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
        
        size_mb = total_size / (1024 * 1024)
        
        if size_mb < 100:  # Same threshold as original
            score = 100
            explanation = f"Repository size is reasonable: {size_mb:.1f} MB"
        elif size_mb < 500:
            score = 70
            explanation = f"Repository is large: {size_mb:.1f} MB"
        else:
            score = 30
            explanation = f"Repository is very large: {size_mb:.1f} MB"
        
        return {
            "score": score,
            "explanation": explanation,
            "evidence": f"{size_mb:.1f} MB"
        }
