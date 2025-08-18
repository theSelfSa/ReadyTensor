"""
Main CLI entry point with .env configuration support
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

from .core.analyzer import RepositoryAnalyzer
from .utils.config import load_config, create_env_file
from .utils.reports import ReportGenerator
from .llm.client import LLMClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup .env file if it doesn't exist"""
    env_file = Path.cwd() / ".env"
    example_file = Path.cwd() / ".env.example"
    
    if not env_file.exists():
        print("No .env file found.")
        
        if example_file.exists():
            print(f"Found .env.example. Copy it to .env and update your API key:")
            print(f"  cp .env.example .env")
        else:
            print("Creating .env template...")
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                create_env_file(api_key)
            else:
                print("API key required. Creating template .env file...")
                create_env_file("sk-your-api-key-here")
        
        return False
    return True

def validate_configuration():
    """Validate configuration and API key"""
    try:
        config = load_config()
        
        # Test API key
        api_key = config.get("openai_api_key")
        if not api_key or api_key == "sk-your-api-key-here":
            print("❌ Please set your OpenAI API key in .env file")
            return False
        
        print("🔑 Testing API key...")
        client = LLMClient(api_key, config.get("openai_model", "gpt-4o-mini"))
        if not client.validate_api_key():
            print("❌ Invalid API key")
            return False
        
        print("✅ Configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main entry point with .env support"""
    parser = argparse.ArgumentParser(description="ReadyTensor Repository Assessment")
    parser.add_argument("repository", nargs="?", help="Repository URL or path") 
    parser.add_argument("--config", help="Additional config file path")
    parser.add_argument("--output-dir", default="data/outputs", help="Output directory")
    parser.add_argument("--setup", action="store_true", help="Setup .env configuration")
    parser.add_argument("--test-config", action="store_true", help="Test configuration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup command
    if args.setup:
        setup_environment()
        return
    
    # Test config command
    if args.test_config:
        if validate_configuration():
            print("✅ All configuration tests passed")
        else:
            sys.exit(1)
        return
    
    # Repository assessment
    if not args.repository:
        print("Usage: ReadyTensor <repository_url_or_path>")
        print("       ReadyTensor --setup     # Create .env file")
        print("       ReadyTensor --test-config  # Test configuration")
        sys.exit(1)
    
    # Check .env file exists
    if not setup_environment():
        print("Please configure .env file first, then run assessment again.")
        sys.exit(1)
    
    # Validate configuration
    if not validate_configuration():
        sys.exit(1)
    
    try:
        # Load configuration
        config = load_config(args.config)
        print(f"🔧 Configuration loaded")
        print(f"   Assessment level: {config.get('assessment_level', 'professional')}")
        print(f"   Model: {config.get('openai_model', 'gpt-4o-mini')}")
        print(f"   Max workers: {config.get('max_workers', 4)}")
        
        # Initialize analyzer  
        analyzer = RepositoryAnalyzer(config)
        
        # Run assessment
        print(f"\n🚀 Starting assessment of {args.repository}")
        results = analyzer.assess_repository(args.repository)
        
        # Generate reports
        report_generator = ReportGenerator(args.output_dir)
        report_generator.generate_reports(results)
        
        print(f"\n✅ Assessment completed successfully")
        print(f"   Overall Score: {results['overall_score']:.1f}/100")
        print(f"   Total Criteria: {results['summary']['total_criteria']}")
        
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
