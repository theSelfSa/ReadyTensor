"""
Main assessment orchestrator - preserves original main.py workflow exactly
Only replaces LangChain calls with direct OpenAI API
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
    """Main assessment orchestrator - mirrors original structure"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize components (replace LangChain with direct API)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
            
        self.llm_client = LLMClient(api_key)
        self.repo_handler = RepositoryHandler()
        
        # Initialize scorers (preserve original logic)
        self.content_scorer = ContentBasedScorer(self.llm_client, config)
        self.metadata_scorer = MetadataBasedScorer(self.llm_client, config) 
        self.logic_validator = LogicBasedValidator(config)
    
    def assess_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Main assessment workflow - exact copy of original main.py sequence
        Only the LLM calls are replaced with direct API
        """
        logger.info(f"Assessing repository: {repo_url}")
        
        # Step 1: Download/clone repository (same as original)
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = self.repo_handler.clone_repository(repo_url, temp_dir)
            
            # Step 2: Run all three assessment types in parallel (preserve original)
            results = {}
            
            with ThreadPoolExecutor(max_workers=self.config.get("max_workers", 4)) as executor:
                # Submit all assessment tasks
                logic_future = executor.submit(self._run_logic_based_assessment, repo_path)
                content_future = executor.submit(self._run_content_based_assessment, repo_path)
                metadata_future = executor.submit(self._run_metadata_based_assessment, repo_path)
                
                # Collect results
                results["logic_based"] = logic_future.result()
                results["content_based"] = content_future.result()
                results["metadata_based"] = metadata_future.result()
            
            # Step 3: Aggregate results (same as original)
            final_results = self._aggregate_results(results, repo_url)
            
        return final_results
    
    def _run_logic_based_assessment(self, repo_path: str) -> Dict[str, Any]:
        """Run logic-based assessment - preserve original generators.py logic"""
        logger.info("Running logic-based assessment")
        return self.logic_validator.assess_repository(repo_path)
    
    def _run_content_based_assessment(self, repo_path: str) -> Dict[str, Any]:
        """Run content-based assessment - replace LangChain with direct API"""
        logger.info("Running content-based assessment") 
        return self.content_scorer.assess_repository(repo_path)
    
    def _run_metadata_based_assessment(self, repo_path: str) -> Dict[str, Any]:
        """Run metadata-based assessment - replace LangChain with direct API"""
        logger.info("Running metadata-based assessment")
        return self.metadata_scorer.assess_repository(repo_path)
    
    def _aggregate_results(self, results: Dict[str, Any], repo_url: str) -> Dict[str, Any]:
        """Aggregate all results - preserve original report.py logic"""
        
        # Combine all criterion results
        all_results = {}
        for assessment_type, type_results in results.items():
            all_results.update(type_results)
        
        # Calculate overall score (same logic as original)
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
                "average_score": overall_score
            }
        }
