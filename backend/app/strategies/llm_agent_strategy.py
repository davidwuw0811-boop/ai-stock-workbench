from app.models.schemas import RiskProfile, StockCandidate, StrategyScore
from app.strategies.base import Strategy, clamp_score


class LLMAgentStrategy(Strategy):
    """Rule-based placeholder for future LLM research agent.

    Future implementation can call OpenAI/Claude/local LLM to synthesize earnings,
    news, filings, and strategy outputs into an explainable research score.
    """

    name = "llm_agent"

    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        sector_bonus = 8 if any(keyword in candidate.sector.lower() for keyword in ["ai", "software", "semiconductor", "半导体", "新能源"]) else 0
        roe = float(candidate.metrics.get("roe", 10))
        growth = float(candidate.metrics.get("revenue_growth", 5))
        sentiment = float(candidate.metrics.get("news_sentiment", 0.5))
        score = 45 + min(roe, 40) * 0.6 + min(growth, 50) * 0.35 + sentiment * 10 + sector_bonus

        rationale = [
            "LLM Agent 投研总结接口已预留",
            f"行业标签：{candidate.sector}",
            "当前基于成长、盈利质量、叙事强度做规则化评分",
        ]
        risks = ["当前未调用真实大模型，建议接入财报、公告、新闻后生成正式投研报告"]

        return StrategyScore(name=self.name, score=clamp_score(score), rationale=rationale, risks=risks)
