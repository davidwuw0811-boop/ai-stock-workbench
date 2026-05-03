from app.models.schemas import RiskProfile, StockCandidate, StrategyScore
from app.strategies.base import Strategy, clamp_score


class FinRLAdapterStrategy(Strategy):
    """Adapter placeholder for FinRL / FinRL-Trading.

    Production idea:
    1. Build market environment with price features and technical indicators.
    2. Train / load DRL agents such as PPO, A2C, SAC, TD3.
    3. Return action probability, allocation signal, or timing confidence.
    """

    name = "finrl"

    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        momentum = float(candidate.metrics.get("six_month_momentum", 0))
        volatility = float(candidate.metrics.get("volatility", 25))
        growth = float(candidate.metrics.get("revenue_growth", 5))

        # Mock timing confidence until a real FinRL agent is connected.
        score = 55 + momentum * 0.45 + growth * 0.25 - max(0, volatility - 35) * 0.25
        rationale = [
            "FinRL 强化学习择时接口已预留",
            "MVP 使用动量、成长和波动率模拟 timing confidence",
        ]
        risks = ["当前为占位策略，未连接真实强化学习模型，不能代表实盘信号"]

        return StrategyScore(name=self.name, score=clamp_score(score), rationale=rationale, risks=risks)
