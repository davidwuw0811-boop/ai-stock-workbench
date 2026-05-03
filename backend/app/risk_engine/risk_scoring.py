from app.models.schemas import RiskProfile, StockCandidate


def build_risk_notes(candidate: StockCandidate, risk_profile: RiskProfile) -> list[str]:
    notes: list[str] = []
    m = candidate.metrics
    pe = float(m.get("pe", 40))
    volatility = float(m.get("volatility", 25))
    debt = float(m.get("debt_to_equity", 0.5))

    if pe > 50:
        notes.append("高估值标的对业绩预期和利率环境更敏感")
    if volatility > 40:
        notes.append("波动率较高，建议结合仓位上限和止损规则")
    if debt > 1:
        notes.append("负债率偏高，需关注现金流和融资成本")
    if risk_profile == RiskProfile.conservative and volatility > 30:
        notes.append("与稳健型风险偏好不完全匹配，需降低仓位或仅作观察")

    return notes or ["暂无明显单项风险，但仍需结合市场环境和组合分散度判断"]


def suitability_text(candidate: StockCandidate, risk_profile: RiskProfile, overall_score: float) -> str:
    if risk_profile == RiskProfile.conservative:
        if overall_score >= 75:
            return "适合稳健型投资者纳入观察池，仍需控制单一持仓比例"
        return "更适合作为研究样本，暂不适合作为稳健型核心标的"
    if risk_profile == RiskProfile.aggressive:
        if overall_score >= 75:
            return "适合激进型投资者关注趋势和催化机会，但需严格风控"
        return "适合小仓位观察或等待更清晰的趋势确认"
    if overall_score >= 80:
        return "适合中长期成长型观察组合"
    if overall_score >= 65:
        return "适合作为候选池标的，需等待估值或趋势确认"
    return "暂不适合作为优先候选标的"
