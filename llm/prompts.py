"""
Prompt templates - port from original config/prompts.yaml
Centralized prompt management
"""

from typing import Dict

class PromptTemplates:
    """Centralized prompt templates"""
    
    CONTENT_ANALYSIS = """
    Analyze the following code/content for quality, best practices, and maintainability:
    
    File: {filename}
    File Type: {file_type}
    Content:
    {content}
    
    Evaluate based on:
    - Code quality and style
    - Documentation and comments  
    - Error handling
    - Best practices adherence
    - Maintainability
    
    Respond in JSON format with:
    - criterion_id: "content_quality"
    - score: integer 0-100
    - explanation: detailed explanation
    - suggestions: list of improvements (optional)
    """
    
    METADATA_ANALYSIS = """
    Analyze this repository's structure, organization, and documentation:
    
    Repository Structure:
    {structure}
    
    README Content:
    {readme_content}
    
    Evaluate:
    - Directory structure and organization
    - Documentation completeness
    - Project clarity and navigability
    - Professional presentation
    
    Respond in JSON format with:
    - criterion_id: "metadata_quality"  
    - score: integer 0-100
    - explanation: detailed assessment
    - recommendations: suggested improvements (optional)
    """
    
    @classmethod
    def get_content_prompt(cls, filename: str, file_type: str, content: str) -> str:
        """Get formatted content analysis prompt"""
        return cls.CONTENT_ANALYSIS.format(
            filename=filename,
            file_type=file_type, 
            content=content
        )
    
    @classmethod
    def get_metadata_prompt(cls, structure: str, readme_content: str) -> str:
        """Get formatted metadata analysis prompt"""
        return cls.METADATA_ANALYSIS.format(
            structure=structure,
            readme_content=readme_content
        )
