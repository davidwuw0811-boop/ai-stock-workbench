from fastapi import APIRouter

from app.models.schemas import Market, ScreeningRequest, ScreeningResponse
from app.services.screening_service import ScreeningService

router = APIRouter()
service = ScreeningService()


@router.get("/markets")
def list_markets() -> dict[str, list[str]]:
    return {"markets": [market.value for market in Market]}


@router.get("/strategies")
def list_strategies() -> dict[str, list[dict[str, str]]]:
    return {
        "strategies": [
            {"name": "fundamental", "label": "基本面多因子", "description": "估值、盈利质量、成长性、资产负债表"},
            {"name": "momentum", "label": "动量趋势", "description": "趋势、波动率、价格强度"},
            {"name": "sentiment", "label": "情绪分析", "description": "新闻、社媒、市场叙事热度"},
            {"name": "finrl", "label": "强化学习择时", "description": "预留 FinRL / FinRL-Trading 接口"},
            {"name": "llm_agent", "label": "LLM 投研 Agent", "description": "预留大模型投研总结接口"},
        ]
    }


@router.post("/screening", response_model=ScreeningResponse)
def screen_stocks(request: ScreeningRequest) -> ScreeningResponse:
    return service.screen(request)
