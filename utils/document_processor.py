import json
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import tiktoken

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Replace LangChain document loaders with native implementations"""
    
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def load_document(self, file_path: str) -> Dict[str, Any]:
        """Load document with metadata - replaces LangChain loaders"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.stat().st_size == 0:
            logger.warning(f"Empty file: {file_path}")
            return {
                'page_content': '',
                'metadata': {'source': str(file_path), 'type': 'empty', 'size': 0}
            }
        
        try:
            if path.suffix == '.py':
                return self._load_python_file(str(path))
            elif path.suffix in ['.md', '.markdown']:
                return self._load_markdown_file(str(path))
            elif path.suffix == '.ipynb':
                return self._load_notebook_file(str(path))
            elif path.suffix in ['.txt', '.yaml', '.yml', '.json', '.toml', '.cfg', '.ini']:
                return self._load_text_file(str(path))
            elif path.suffix in ['.rst', '.tex']:
                return self._load_text_file(str(path))
            else:
                # Try to load as text file
                return self._load_text_file(str(path))
                
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            raise Exception(f"Error loading {file_path}: {str(e)}")
    
    def _load_python_file(self, file_path: str) -> Dict[str, Any]:
        """Load Python source file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'page_content': content,
            'metadata': {
                'source': file_path,
                'type': 'python',
                'size': len(content),
                'lines': len(content.split('\n'))
            }
        }
    
    def _load_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Load Markdown file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'page_content': content,
            'metadata': {
                'source': file_path,
                'type': 'markdown',
                'size': len(content),
                'lines': len(content.split('\n'))
            }
        }
    
    def _load_notebook_file(self, file_path: str) -> Dict[str, Any]:
        """Load Jupyter notebook and extract content"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                notebook = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid notebook JSON: {file_path}")
                raise ValueError(f"Invalid notebook format: {e}")
        
        # Extract content from cells
        content_parts = []
        code_cells = 0
        markdown_cells = 0
        
        for cell in notebook.get('cells', []):
            cell_type = cell.get('cell_type', '')
            source = cell.get('source', [])
            
            if isinstance(source, list):
                cell_content = ''.join(source)
            else:
                cell_content = str(source)
            
            if cell_type == 'code':
                content_parts.append(f"# Code Cell\n{cell_content}")
                code_cells += 1
            elif cell_type == 'markdown':
                content_parts.append(f"# Markdown Cell\n{cell_content}")
                markdown_cells += 1
            
            content_parts.append('\n' + '='*50 + '\n')
        
        full_content = '\n'.join(content_parts)
        
        return {
            'page_content': full_content,
            'metadata': {
                'source': file_path,
                'type': 'notebook',
                'size': len(full_content),
                'code_cells': code_cells,
                'markdown_cells': markdown_cells
            }
        }
    
    def _load_text_file(self, file_path: str) -> Dict[str, Any]:
        """Load generic text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not decode file: {file_path}")
        
        file_type = Path(file_path).suffix[1:] if Path(file_path).suffix else 'text'
        
        return {
            'page_content': content,
            'metadata': {
                'source': file_path,
                'type': file_type,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
        }
    
    def chunk_text(self, text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
        """Replace LangChain RecursiveCharacterTextSplitter"""
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find end position
            end = start + chunk_size
            
            if end >= len(text):
                # Last chunk
                chunks.append(text[start:])
                break
            
            # Try to break at natural boundaries
            break_chars = ['\n\n', '\n', '. ', '! ', '? ', '; ', ', ']
            best_break = end
            
            for break_char in break_chars:
                last_break = text.rfind(break_char, start, end)
                if last_break > start:
                    best_break = last_break + len(break_char)
                    break
            
            chunks.append(text[start:best_break])
            
            # Move start position with overlap
            start = best_break - overlap if best_break - overlap > start else best_break
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback: rough approximation
            return len(text.split()) * 1.3
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to maximum token count"""
        if self.count_tokens(text) <= max_tokens:
            return text
        
        # Binary search for the right length
        start, end = 0, len(text)
        
        while start < end:
            mid = (start + end + 1) // 2
            if self.count_tokens(text[:mid]) <= max_tokens:
                start = mid
            else:
                end = mid - 1
        
        return text[:start]
