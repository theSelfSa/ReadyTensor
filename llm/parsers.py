"""
Response parsing models - exact copy from original output_parsers.py
Preserve all Pydantic models for structured responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CriterionResponse(BaseModel):
    """Individual criterion assessment response"""
    criterion_id: str = Field(description="Unique identifier for criterion")
    score: int = Field(ge=0, le=100, description="Score between 0-100")
    explanation: str = Field(description="Detailed explanation of the score")
    evidence: Optional[List[str]] = Field(default=None, description="Supporting evidence")
    suggestions: Optional[List[str]] = Field(default=None, description="Improvement suggestions")

class ContentAnalysisResponse(BaseModel):
    """Content analysis response"""
    file_path: str = Field(description="Path to analyzed file")
    overall_score: int = Field(ge=0, le=100, description="Overall file score")
    criteria_results: List[CriterionResponse] = Field(description="Individual criterion results")
    summary: str = Field(description="Assessment summary")

class MetadataAnalysisResponse(BaseModel):
    """Metadata analysis response"""
    repository_structure_score: int = Field(ge=0, le=100, description="Structure quality score")
    documentation_score: int = Field(ge=0, le=100, description="Documentation quality score")
    organization_score: int = Field(ge=0, le=100, description="Organization score")
    overall_score: int = Field(ge=0, le=100, description="Overall metadata score")
    explanation: str = Field(description="Detailed explanation")
    recommendations: Optional[List[str]] = Field(default=None, description="Improvement recommendations")
