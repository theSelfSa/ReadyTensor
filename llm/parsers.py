"""
Pydantic models for structured responses
Copy from original rt-repo-assessment/src/output_parsers.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class CriterionResponse(BaseModel):
    """Response model for individual criterion assessment"""
    criterion_id: str = Field(description="Unique identifier for the criterion")
    score: int = Field(ge=0, le=100, description="Score between 0-100")
    explanation: str = Field(description="Detailed explanation of the score")
    evidence: Optional[List[str]] = Field(default=None, description="Supporting evidence")
    suggestions: Optional[List[str]] = Field(default=None, description="Improvement suggestions")

class ContentBasedResponse(BaseModel):
    """Response for content-based file assessment"""
    file_path: str = Field(description="Path to the assessed file")
    criteria_results: List[CriterionResponse] = Field(description="Results for each criterion")
    overall_score: int = Field(ge=0, le=100, description="Overall file score")
    summary: str = Field(description="Summary of assessment")

class MetadataBasedResponse(BaseModel):
    """Response for metadata/structure assessment"""
    criterion_id: str = Field(description="Criterion identifier")
    score: int = Field(ge=0, le=100, description="Assessment score")
    explanation: str = Field(description="Detailed explanation")
    repository_structure: Optional[Dict[str, Any]] = Field(default=None, description="Structure analysis")

class LogicBasedResponse(BaseModel):
    """Response for logic-based assessment"""
    criterion_id: str = Field(description="Criterion identifier")
    passed: bool = Field(description="Whether criterion was met")
    score: int = Field(ge=0, le=100, description="Assessment score")
    details: str = Field(description="Assessment details")
    evidence: Optional[Dict[str, Any]] = Field(default=None, description="Evidence found")

class AssessmentReport(BaseModel):
    """Complete assessment report"""
    repository_url: str = Field(description="Repository URL or path")
    overall_score: int = Field(ge=0, le=100, description="Overall assessment score")
    category_scores: Dict[str, Dict[str, Union[int, str]]] = Field(description="Scores by category")
    detailed_results: List[Union[CriterionResponse, ContentBasedResponse, MetadataBasedResponse]] = Field(description="Detailed assessment results")
    summary: str = Field(description="Assessment summary")
    timestamp: str = Field(description="Assessment timestamp")
