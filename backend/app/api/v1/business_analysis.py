from fastapi import APIRouter, Depends
from app.schemas.analysis import AnalysisRunRequest, BusinessAnalysisResponse
from app.schemas.auth import UserResponse
from app.schemas.common import ResponseModel
from app.middleware.auth_middleware import get_current_user
from app.utils.data_processing import extract_summary
from app.api.v1.analysis import get_dataframe, sync_analysis_to_firestore
from app.services.business_analysis_service import business_analysis_service

router = APIRouter()

# Distinct Endpoint: POST /api/v1/business-analysis/statistical-insights
@router.post("/statistical-insights", response_model=ResponseModel[BusinessAnalysisResponse])
async def run_business_analysis(req: AnalysisRunRequest, current_user: UserResponse = Depends(get_current_user)):
    df = get_dataframe(req.file_id)
    summary = extract_summary(df)
    bus_analysis = business_analysis_service.generate_business_analysis(summary, api_key=req.api_key)
    
    sync_analysis_to_firestore(req.file_id, current_user.user_id, {
        "business_analysis": bus_analysis
    })
    
    return ResponseModel(success=True, message="Output 2 Statistical & Business Analysis generated successfully", data=BusinessAnalysisResponse(file_id=req.file_id, business_analysis=bus_analysis))