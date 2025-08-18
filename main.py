"""Main CLI entry point - mirrors original main.py workflow"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

from .core.analyzer import RepositoryAnalyzer
from .utils.config import load_config
from .utils.reports import ReportGenerator

# Setup logging exactly like original
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point - preserve original main.py structure"""
    parser = argparse.ArgumentParser(description="ReadyTensor Repository Assessment")
    parser.add_argument("repository", nargs="?", help="Repository URL or path") 
    parser.add_argument("--config", default="config.json", help="Config file path")
    parser.add_argument("--output-dir", default="data/outputs", help="Output directory")
    
    args = parser.parse_args()
    
    if not args.repository:
        print("Usage: ReadyTensor <repository_url_or_path>")
        sys.exit(1)
    
    try:
        # Load configuration (same as original)
        config = load_config(args.config)
        
        # Initialize analyzer  
        analyzer = RepositoryAnalyzer(config)
        
        # Run assessment (preserve original workflow)
        logger.info(f"Starting assessment of {args.repository}")
        results = analyzer.assess_repository(args.repository)
        
        # Generate reports (same format as original)
        report_generator = ReportGenerator(args.output_dir)
        report_generator.generate_reports(results)
        
        logger.info("Assessment completed successfully")
        
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
