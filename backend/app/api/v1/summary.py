from fastapi import APIRouter, Depends
from app.schemas.analysis import ExecutiveSummaryRequest, ExecutiveSummaryResponse
from app.schemas.auth import UserResponse
from app.schemas.common import ResponseModel
from app.middleware.auth_middleware import get_current_user
from app.utils.data_processing import extract_summary
from app.api.v1.analysis import get_dataframe, sync_analysis_to_firestore
from app.services.business_analysis_service import business_analysis_service
from app.services.summary_service import summary_service

router = APIRouter()

# Distinct Endpoint: POST /api/v1/summary/executive-strategy
@router.post("/executive-strategy", response_model=ResponseModel[ExecutiveSummaryResponse])
async def run_executive_summary(req: ExecutiveSummaryRequest, current_user: UserResponse = Depends(get_current_user)):
    df = get_dataframe(req.file_id)
    summary = extract_summary(df)
    bus_analysis = req.business_analysis or ""
    if not bus_analysis:
        bus_analysis = business_analysis_service.generate_business_analysis(summary, api_key=req.api_key)
        
    exec_strat = summary_service.generate_executive_summary(summary, bus_analysis, api_key=req.api_key)
    
    sync_analysis_to_firestore(req.file_id, current_user.user_id, {
        "executive_strategy": exec_strat
    })
    
    return ResponseModel(success=True, message="Output 4 Executive Summary & Action Plan generated successfully", data=ExecutiveSummaryResponse(file_id=req.file_id, executive_strategy=exec_strat))