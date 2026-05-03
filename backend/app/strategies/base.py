from abc import ABC, abstractmethod

from app.models.schemas import RiskProfile, StockCandidate, StrategyScore


class Strategy(ABC):
    name: str

    @abstractmethod
    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        """Score a stock candidate from 0 to 100."""


def clamp_score(value: float) -> float:
    return max(0.0, min(100.0, round(value, 2)))
