"""
File operations - lightweight implementation
Basic file handling without heavy dependencies
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional

def ensure_directory(directory: str) -> None:
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)

def get_file_extension(file_path: str) -> str:
    """Get file extension"""
    return Path(file_path).suffix.lower()

def read_text_file(file_path: str) -> str:
    """Read text file with encoding handling"""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Could not read file: {file_path}")

def write_text_file(file_path: str, content: str) -> None:
    """Write text file"""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def copy_file(source: str, destination: str) -> None:
    """Copy file"""
    ensure_directory(os.path.dirname(destination))
    shutil.copy2(source, destination)
