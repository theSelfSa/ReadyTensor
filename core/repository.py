"""
Repository operations - port from original utils/repository.py
Keep exact same functionality, just lighter dependencies
"""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import subprocess
import logging

logger = logging.getLogger(__name__)

class RepositoryHandler:
    """Handle repository cloning and file operations"""
    
    def clone_repository(self, repo_url: str, target_dir: str) -> str:
        """
        Clone repository - preserve original logic from utils/repository.py
        Support both git clone and zip download
        """
        if os.path.exists(repo_url):
            # Local directory
            repo_name = Path(repo_url).name
            target_path = os.path.join(target_dir, repo_name)
            shutil.copytree(repo_url, target_path)
            logger.info(f"Copied local repository to {target_path}")
            return target_path
        
        elif repo_url.startswith(("http://", "https://")):
            # Remote repository
            if "github.com" in repo_url:
                return self._download_github_repo(repo_url, target_dir)
            else:
                return self._git_clone(repo_url, target_dir)
        
        else:
            raise ValueError(f"Invalid repository URL or path: {repo_url}")
    
    def _download_github_repo(self, repo_url: str, target_dir: str) -> str:
        """Download GitHub repo as ZIP - same logic as original"""
        import requests
        
        # Convert GitHub URL to ZIP download
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        zip_url = f"{repo_url}/archive/refs/heads/main.zip"
        
        # Extract repo name for directory
        repo_name = repo_url.split('/')[-1]
        target_path = os.path.join(target_dir, repo_name)
        
        logger.info(f"Downloading repository from {zip_url}")
        
        # Download and extract
        response = requests.get(zip_url)
        response.raise_for_status()
        
        zip_path = os.path.join(target_dir, "repo.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        
        # Find extracted directory (usually repo-name-main)
        extracted_dirs = [d for d in os.listdir(target_dir) 
                         if os.path.isdir(os.path.join(target_dir, d)) and d != repo_name]
        
        if extracted_dirs:
            # Move extracted content to target path
            shutil.move(os.path.join(target_dir, extracted_dirs[0]), target_path)
        
        # Cleanup
        os.remove(zip_path)
        
        logger.info(f"Repository downloaded to {target_path}")
        return target_path
    
    def _git_clone(self, repo_url: str, target_dir: str) -> str:
        """Git clone fallback"""
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        target_path = os.path.join(target_dir, repo_name)
        
        subprocess.run(['git', 'clone', repo_url, target_path], check=True)
        logger.info(f"Git cloned repository to {target_path}")
        return target_path
    
    def get_file_list(self, repo_path: str, extensions: Optional[List[str]] = None) -> List[str]:
        """Get file list - same logic as original"""
        if extensions is None:
            extensions = ['.py', '.md', '.ipynb', '.txt', '.yaml', '.yml', '.json']
        
        files = []
        for root, dirs, filenames in os.walk(repo_path):
            # Skip common directories (same as original)
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in {'__pycache__', 'node_modules', '.git'}]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
        
        return files
