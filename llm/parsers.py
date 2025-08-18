# ReadyTensor/llm/parsers.py

import json
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional, Dict, Any, Union

class CriterionResponse(BaseModel):
    """Response model for individual criterion assessment"""
    criterion_id: str = Field(description="Unique identifier for the criterion")
    score: int = Field(ge=0, le=100, description="Score between 0-100")
    explanation: Union[str, Dict[str, Any]] = Field(description="Detailed explanation of the score")
    evidence: Optional[List[str]] = Field(default=None, description="Supporting evidence")
    suggestions: Optional[List[str]] = Field(default=None, description="Improvement suggestions")

    @root_validator(pre=True)
    def normalize_explanation(cls, values):
        exp = values.get("explanation")
        if isinstance(exp, dict):
            try:
                # Convert dict to formatted JSON string
                values["explanation"] = json.dumps(exp, indent=2)
            except Exception:
                # Fallback to simple str()
                values["explanation"] = str(exp)
        return values


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
    explanation: Union[str, Dict[str, Any]] = Field(description="Detailed explanation")
    recommendations: Optional[List[str]] = Field(default=None, description="Improvement recommendations")

    @root_validator(pre=True)
    def normalize_explanation(cls, values):
        exp = values.get("explanation")
        if isinstance(exp, dict):
            try:
                values["explanation"] = json.dumps(exp, indent=2)
            except Exception:
                values["explanation"] = str(exp)
        return values
