import os
import json
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from ..llm.client import LLMClient
from ..llm.parsers import CriterionResponse

logger = logging.getLogger(__name__)

class ContentBasedScorer:
    """Content-based scoring with chunking and aggregation"""

    def __init__(self, llm_client: LLMClient, config: Dict[str, Any]):
        self.llm_client = llm_client
        self.config = config
        self.max_workers = config.get("max_workers", 4)
        self.token_limit = config.get("token_limit", 8000)

    def assess_repository(self, repo_path: str) -> Dict[str, Any]:
        """Assess repository content - preserve original logic with chunking"""
        files_to_assess = self._get_assessable_files(repo_path)
        logger.info(f"Assessing {len(files_to_assess)} files")
        results: Dict[str, Any] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._assess_file, file_path): file_path
                for file_path in files_to_assess
            }
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    results[file_path] = future.result()
                except Exception as e:
                    logger.error(f"Error assessing {file_path}: {e}")
                    results[file_path] = {"score": 0, "error": str(e)}

        return results

    def _get_assessable_files(self, repo_path: str) -> List[str]:
        """Get files for assessment - same filtering as original"""
        extensions = ['.py', '.md', '.ipynb', '.txt']
        files: List[str] = []
        for root, dirs, filenames in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'node_modules'}]
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, filename)
                    if os.path.getsize(file_path) < 1024 * 1024:  # 1MB limit
                        files.append(file_path)
        return files

    def _assess_file(self, file_path: str) -> Dict[str, Any]:
        """Assess individual file - chunk content instead of truncation"""
        content = self._load_file_content(file_path)
        if not content.strip():
            return {"file_path": file_path, "score": 0, "explanation": "Empty file"}

        # Split into overlapping chunks to cover entire content
        chunks = self._chunk_text(content)
        chunk_results: List[Dict[str, Any]] = []

        for chunk in chunks:
            prompt = self._create_assessment_prompt(chunk, file_path)
            response = self.llm_client.invoke_structured(prompt, CriterionResponse)
            chunk_results.append(response)

        # Aggregate numeric scores
        scores = [r.get("score", 0) for r in chunk_results]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Aggregate explanations: pick the longest three
        explanations = sorted(
            (r.get("explanation", "") for r in chunk_results),
            key=len, reverse=True
        )[:3]
        explanation = "\n\n".join(explanations)

        return {
            "file_path": file_path,
            "score": avg_score,
            "explanation": explanation
        }

    def _load_file_content(self, file_path: str) -> str:
        """Load file content - replace LangChain loaders"""
        if file_path.endswith('.ipynb'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                notebook = json.load(f)
            content = ""
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') in ['code', 'markdown']:
                    source = cell.get('source', [])
                    if isinstance(source, list):
                        content += ''.join(source) + '\n\n'
            return content
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks based on token limit"""
        # Estimate character-based chunk size roughly proportional to token limit
        approx_char_limit = int(self.token_limit * 4)
        overlap_chars = int(approx_char_limit * 0.1)
        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = min(start + approx_char_limit, len(text))
            chunks.append(text[start:end])
            start = end - overlap_chars
        return chunks

    def _create_assessment_prompt(self, content: str, file_path: str) -> str:
        """Create assessment prompt - same format as original"""
        file_type = Path(file_path).suffix
        return f"""
Analyze the following {file_type} file for code quality and best practices:

File: {os.path.basename(file_path)}
Content:
{content}

Provide assessment as JSON with fields:
- criterion_id: "content_quality"
- score: (0-100)
- explanation: (detailed explanation)
"""

class MetadataBasedScorer:
    """Metadata-based scoring - replace LangChain with direct API"""

    def __init__(self, llm_client: LLMClient, config: Dict[str, Any]):
        self.llm_client = llm_client
        self.config = config

    def assess_repository(self, repo_path: str) -> Dict[str, Any]:
        """Assess repository metadata - preserve original logic"""
        repo_structure = self._generate_repo_structure(repo_path)
        readme_content = self._read_readme(repo_path)
        prompt = self._create_metadata_prompt(repo_structure, readme_content)

        try:
            response = self.llm_client.invoke_structured(prompt, CriterionResponse)
            logger.info(f"Metadata assessment complete: {response.get('score', 0)}")
            return {"metadata_assessment": response}
        except Exception as e:
            logger.error(f"Metadata assessment failed: {e}")
            return {"metadata_assessment": {"score": 0, "error": str(e)}}

    def _generate_repo_structure(self, repo_path: str) -> str:
        """Generate repository structure tree - same as original tree.py"""
        structure: List[str] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            level = root.replace(repo_path, '').count(os.sep)
            indent = '  ' * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for file in sorted(files):
                if not file.startswith('.'):
                    structure.append(f"{subindent}{file}")
        return '\n'.join(structure)

    def _read_readme(self, repo_path: str) -> str:
        """Read README content - same logic as original"""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        for readme_file in readme_files:
            path = os.path.join(repo_path, readme_file)
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except Exception:
                    continue
        return "No README found"

    def _create_metadata_prompt(self, structure: str, readme: str) -> str:
        """Create metadata assessment prompt"""
        return f"""
Analyze this repository's structure and documentation:

Repository Structure:
{structure}

README Content:
{readme}

Assess the repository organization, structure, and documentation quality.
Provide assessment as JSON with fields:
- criterion_id: "metadata_quality"
- score: (0-100)
- explanation: (detailed explanation)
"""
