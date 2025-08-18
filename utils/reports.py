"""
Report generation - exact port from original report.py
Preserve all report formats and structure
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from .file_ops import ensure_directory, write_text_file

class ReportGenerator:
    """Generate assessment reports - same format as original"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        ensure_directory(output_dir)
    
    def generate_reports(self, assessment_results: Dict[str, Any]) -> None:
        """Generate all report formats - preserve original report.py logic"""
        
        repo_name = self._extract_repo_name(assessment_results["repository_url"])
        timestamp = datetime.now().isoformat()
        
        # Generate JSON report (same structure as original)
        json_report = self._generate_json_report(assessment_results, timestamp)
        json_path = os.path.join(self.output_dir, f"{repo_name}_assessment.json")
        write_text_file(json_path, json.dumps(json_report, indent=2))
        
        # Generate Markdown report (same format as original)
        md_report = self._generate_markdown_report(assessment_results, timestamp)
        md_path = os.path.join(self.output_dir, f"{repo_name}_report.md")
        write_text_file(md_path, md_report)
        
        print(f"Reports generated:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        if repo_url.startswith("http"):
            return repo_url.split('/')[-1].replace('.git', '')
        else:
            return os.path.basename(repo_url)
    
    def _generate_json_report(self, results: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        """Generate JSON report - same structure as original"""
        return {
            "assessment_metadata": {
                "repository_url": results["repository_url"],
                "timestamp": timestamp,
                "overall_score": results["overall_score"]
            },
            "summary": results["summary"],
            "detailed_results": results["detailed_results"]
        }
    
    def _generate_markdown_report(self, results: Dict[str, Any], timestamp: str) -> str:
        """Generate Markdown report - same format as original report.py"""
        
        repo_name = self._extract_repo_name(results["repository_url"])
        overall_score = results["overall_score"]
        
        md_content = f"""# Repository Assessment Report

## Repository Information
- **Repository**: {results["repository_url"]}
- **Assessment Date**: {timestamp}
- **Overall Score**: {overall_score:.1f}/100

## Summary
- Total Criteria Assessed: {results["summary"]["total_criteria"]}
- Average Score: {results["summary"]["average_score"]:.1f}

## Detailed Results

"""
        
        # Add detailed results (preserve original formatting)
        for criterion_id, result in results["detailed_results"].items():
            if isinstance(result, dict) and "score" in result:
                score = result["score"]
                explanation = result.get("explanation", "No explanation provided")
                
                md_content += f"### {criterion_id}\n"
                md_content += f"**Score**: {score}/100\n\n"
                md_content += f"**Explanation**: {explanation}\n\n"
                
                if "evidence" in result and result["evidence"]:
                    md_content += f"**Evidence**: {result['evidence']}\n\n"
                
                md_content += "---\n\n"
        
        return md_content
