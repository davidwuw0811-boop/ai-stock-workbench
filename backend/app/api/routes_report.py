from fastapi import APIRouter, HTTPException

from app.core.disclaimers import RESEARCH_DISCLAIMER_ZH
from app.models.schemas import ReportRequest, ReportResponse, ScreeningRequest
from app.report_generator.report_builder import build_markdown_report
from app.services.screening_service import ScreeningService

router = APIRouter()
service = ScreeningService()


@router.post("/report", response_model=ReportResponse)
def generate_report(request: ReportRequest) -> ReportResponse:
    screening = service.screen(
        ScreeningRequest(
            market=request.market,
            risk_profile=request.risk_profile,
            strategies=["fundamental", "momentum", "sentiment", "finrl", "llm_agent"],
            top_n=20,
        )
    )
    matched = next((item for item in screening.results if item.ticker.upper() == request.ticker.upper()), None)
    if matched is None:
        raise HTTPException(status_code=404, detail="Ticker not found in MVP mock universe")

    return ReportResponse(
        ticker=matched.ticker,
        market=matched.market,
        markdown_report=build_markdown_report(matched, RESEARCH_DISCLAIMER_ZH),
        disclaimer=RESEARCH_DISCLAIMER_ZH,
    )
