from app.models.schemas import RiskProfile, StockCandidate, StrategyScore
from app.strategies.base import Strategy, clamp_score


class MomentumStrategy(Strategy):
    name = "momentum"

    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        momentum = float(candidate.metrics.get("six_month_momentum", 0))
        volatility = float(candidate.metrics.get("volatility", 25))

        raw = 50 + momentum * 1.1
        if risk_profile == RiskProfile.conservative:
            raw -= max(0, volatility - 25) * 0.9
        elif risk_profile == RiskProfile.balanced:
            raw -= max(0, volatility - 35) * 0.5
        else:
            raw -= max(0, volatility - 50) * 0.25

        rationale = [
            f"近 6 个月动量 {momentum:.1f}%",
            f"波动率 {volatility:.1f}% 用于风险惩罚",
        ]
        risks: list[str] = []
        if momentum > 35:
            risks.append("短期涨幅较大，可能存在拥挤交易和回撤风险")
        if volatility > 40:
            risks.append("波动率较高，仓位管理要求更高")
        if momentum < 0:
            risks.append("动量为负，趋势尚未确认")

        return StrategyScore(name=self.name, score=clamp_score(raw), rationale=rationale, risks=risks)
