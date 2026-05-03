from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Market(str, Enum):
    US = "US"
    CN = "CN"


class RiskProfile(str, Enum):
    conservative = "conservative"
    balanced = "balanced"
    aggressive = "aggressive"


StrategyName = Literal["fundamental", "momentum", "sentiment", "finrl", "llm_agent"]


class ScreeningRequest(BaseModel):
    market: Market = Market.US
    strategies: list[StrategyName] = Field(default_factory=lambda: ["fundamental", "momentum", "sentiment"])
    risk_profile: RiskProfile = RiskProfile.balanced
    top_n: int = Field(default=5, ge=1, le=20)


class StockCandidate(BaseModel):
    ticker: str
    name: str
    market: Market
    sector: str
    price: float
    currency: str
    metrics: dict[str, float | str]


class StrategyScore(BaseModel):
    name: str
    score: float = Field(ge=0, le=100)
    rationale: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class ScreeningResult(BaseModel):
    ticker: str
    name: str
    market: Market
    sector: str
    price: float
    currency: str
    overall_score: float
    strategy_scores: dict[str, float]
    thesis: list[str]
    risks: list[str]
    suitability: str


class ScreeningResponse(BaseModel):
    market: Market
    risk_profile: RiskProfile
    results: list[ScreeningResult]
    disclaimer: str


class ReportRequest(BaseModel):
    ticker: str
    market: Market = Market.US
    risk_profile: RiskProfile = RiskProfile.balanced


class ReportResponse(BaseModel):
    ticker: str
    market: Market
    markdown_report: str
    disclaimer: str


class BacktestRequest(BaseModel):
    market: Market = Market.US
    strategy: StrategyName = "fundamental"
    start_date: str = "2023-01-01"
    end_date: str = "2025-12-31"
    initial_cash: float = 100000


class BacktestResponse(BaseModel):
    market: Market
    strategy: str
    start_date: str
    end_date: str
    initial_cash: float
    final_value: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    turnover: float
    note: str
