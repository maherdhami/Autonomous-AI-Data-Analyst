from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AnalysisModel(BaseModel):
    analysis_id: str
    user_id: str
    file_id: str
    filename: str
    file_metadata: Dict[str, Any]
    quality_assessment: str
    business_analysis: str
    executive_strategy: str
    quality_score: int = 85
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    dataset_summary: Dict[str, Any] = Field(default_factory=dict)
    created_at: int
    updated_at: int
