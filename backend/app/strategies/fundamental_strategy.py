from app.models.schemas import RiskProfile, StockCandidate, StrategyScore
from app.strategies.base import Strategy, clamp_score


class FundamentalStrategy(Strategy):
    name = "fundamental"

    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        m = candidate.metrics
        pe = float(m.get("pe", 40))
        roe = float(m.get("roe", 10))
        growth = float(m.get("revenue_growth", 5))
        margin = float(m.get("gross_margin", 30))
        debt = float(m.get("debt_to_equity", 0.5))

        valuation_score = 100 - min(pe, 90) * 0.8
        quality_score = min(roe * 2.0, 100)
        growth_score = min(growth * 2.0, 100)
        margin_score = min(margin, 100)
        debt_score = 100 - min(debt * 30, 60)

        if risk_profile == RiskProfile.conservative:
            score = valuation_score * 0.25 + quality_score * 0.3 + growth_score * 0.15 + margin_score * 0.15 + debt_score * 0.15
        elif risk_profile == RiskProfile.aggressive:
            score = valuation_score * 0.15 + quality_score * 0.2 + growth_score * 0.35 + margin_score * 0.15 + debt_score * 0.15
        else:
            score = valuation_score * 0.2 + quality_score * 0.25 + growth_score * 0.25 + margin_score * 0.15 + debt_score * 0.15

        rationale = [
            f"ROE {roe:.1f}% 反映盈利质量",
            f"营收增长 {growth:.1f}% 反映成长性",
            f"PE {pe:.1f} 用于估值约束",
        ]
        risks: list[str] = []
        if pe > 50:
            risks.append("估值较高，需警惕业绩不及预期引发的估值压缩")
        if debt > 1:
            risks.append("杠杆水平偏高，需关注利率和现金流压力")
        if growth < 8:
            risks.append("成长性偏弱，需关注收入增长放缓")

        return StrategyScore(name=self.name, score=clamp_score(score), rationale=rationale, risks=risks)
