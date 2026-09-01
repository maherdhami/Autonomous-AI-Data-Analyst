from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class FileMetadata(BaseModel):
    file_id: str
    filename: str
    size_bytes: int
    rows: int
    columns_count: int
    columns: List[str]

class ChartConfig(BaseModel):
    chart_type: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    aggregation: Optional[str] = "sum"
    title: str
    business_reason: Optional[str] = None
    plotly_json: Optional[Dict[str, Any]] = None

class AnalysisRunRequest(BaseModel):
    file_id: str
    api_key: Optional[str] = None

class ExecutiveSummaryRequest(BaseModel):
    file_id: str
    business_analysis: Optional[str] = ""
    api_key: Optional[str] = None

# Single Responsibility Output Responses matching UI
class QualityAssessmentResponse(BaseModel):
    file_id: str
    quality_assessment: str
    quality_score: int = 85

class BusinessAnalysisResponse(BaseModel):
    file_id: str
    business_analysis: str

class VisualizationsResponse(BaseModel):
    file_id: str
    charts: List[ChartConfig]

class ExecutiveSummaryResponse(BaseModel):
    file_id: str
    executive_strategy: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    user_id: str
    file_metadata: FileMetadata
    quality_assessment: str
    business_analysis: str
    executive_strategy: str
    quality_score: int = 85
    charts: List[ChartConfig] = []
    created_at: int
    dataset_summary: Optional[Dict[str, Any]] = None
