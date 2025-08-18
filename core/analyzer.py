"""
Main assessment orchestrator with .env configuration support
"""

import os
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Tuple
import logging

from ..llm.client import LLMClient
from ..utils.config import load_config
from .repository import RepositoryHandler
from .scorer import ContentBasedScorer, MetadataBasedScorer
from .validators import LogicBasedValidator

logger = logging.getLogger(__name__)

class RepositoryAnalyzer:
    """Main assessment orchestrator with .env configuration"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Load configuration (includes .env loading)
        self.config = config or load_config()
        
        # Validate API key from config
        api_key = self.config.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not found in configuration. Check your .env file.")
            
        # Initialize components
        model = self.config.get("openai_model", "gpt-4o-mini")
        self.llm_client = LLMClient(api_key, model)
        self.repo_handler = RepositoryHandler()
        
        # Initialize scorers
        self.content_scorer = ContentBasedScorer(self.llm_client, self.config)
        self.metadata_scorer = MetadataBasedScorer(self.llm_client, self.config) 
        self.logic_validator = LogicBasedValidator(self.config)
        
        logger.info(f"Initialized with model: {model}")
        logger.info(f"Max workers: {self.config.get('max_workers', 4)}")
    
    def assess_repository(self, repo_url: str) -> Dict[str, Any]:
        """Main assessment workflow with configuration from .env"""
        logger.info(f"Assessing repository: {repo_url}")
        logger.info(f"Assessment level: {self.config.get('assessment_level', 'professional')}")
        
        # Step 1: Download/clone repository
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = self.repo_handler.clone_repository(repo_url, temp_dir)
            
            # Step 2: Run all assessments in parallel
            results = {}
            
            with ThreadPoolExecutor(max_workers=self.config.get("max_workers", 4)) as executor:
                # Submit assessment tasks
                logic_future = executor.submit(self._run_logic_based_assessment, repo_path)
                content_future = executor.submit(self._run_content_based_assessment, repo_path)
                metadata_future = executor.submit(self._run_metadata_based_assessment, repo_path)
                
                # Collect results
                results["logic_based"] = logic_future.result()
                results["content_based"] = content_future.result()
                results["metadata_based"] = metadata_future.result()
            
            # Step 3: Aggregate results
            final_results = self._aggregate_results(results, repo_url)
            
        return final_results
    
    def _run_logic_based_assessment(self, repo_path: str) -> Dict[str, Any]:
        """Run logic-based assessment"""
        logger.info("Running logic-based assessment")
        return self.logic_validator.assess_repository(repo_path)
    
    def _run_content_based_assessment(self, repo_path: str) -> Dict[str, Any]:
        """Run content-based assessment"""
        logger.info("Running content-based assessment") 
        return self.content_scorer.assess_repository(repo_path)
    
    def _run_metadata_based_assessment(self, repo_path: str) -> Dict[str, Any]:
        """Run metadata-based assessment"""
        logger.info("Running metadata-based assessment")
        return self.metadata_scorer.assess_repository(repo_path)
    
    def _aggregate_results(self, results: Dict[str, Any], repo_url: str) -> Dict[str, Any]:
        """Aggregate all results"""
        
        # Combine all criterion results
        all_results = {}
        for assessment_type, type_results in results.items():
            all_results.update(type_results)
        
        # Calculate overall score
        total_score = 0
        total_criteria = 0
        
        for criterion_id, result in all_results.items():
            if isinstance(result, dict) and "score" in result:
                total_score += result["score"]
                total_criteria += 1
        
        overall_score = total_score / total_criteria if total_criteria > 0 else 0
        
        return {
            "repository_url": repo_url,
            "overall_score": overall_score,
            "detailed_results": all_results,
            "summary": {
                "total_criteria": total_criteria,
                "average_score": overall_score,
                "assessment_level": self.config.get("assessment_level", "professional")
            }
        }
