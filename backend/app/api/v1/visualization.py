from fastapi import APIRouter, Depends
from app.schemas.analysis import AnalysisRunRequest, VisualizationsResponse, ChartConfig
from app.schemas.auth import UserResponse
from app.schemas.common import ResponseModel
from app.middleware.auth_middleware import get_current_user
from app.utils.data_processing import extract_summary
from app.api.v1.analysis import get_dataframe, sync_analysis_to_firestore
from app.services.visualization_service import visualization_service

router = APIRouter()

# Distinct Endpoint: POST /api/v1/visualization/generate-charts
@router.post("/generate-charts", response_model=ResponseModel[VisualizationsResponse])
async def run_visualizations(req: AnalysisRunRequest, current_user: UserResponse = Depends(get_current_user)):
    df = get_dataframe(req.file_id)
    summary = extract_summary(df)
    charts = visualization_service.generate_visualizations(summary, df, api_key=req.api_key)
    
    sync_analysis_to_firestore(req.file_id, current_user.user_id, {
        "charts": charts
    })
    
    return ResponseModel(success=True, message="Output 3 Recommended Visualizations generated successfully", data=VisualizationsResponse(file_id=req.file_id, charts=[ChartConfig(**c) for c in charts]))