from app.models.schemas import RiskProfile, StockCandidate, StrategyScore
from app.strategies.base import Strategy, clamp_score


class SentimentStrategy(Strategy):
    name = "sentiment"

    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        sentiment = float(candidate.metrics.get("news_sentiment", 0.5))
        score = 35 + sentiment * 65

        rationale = [
            f"新闻/社媒情绪模拟值 {sentiment:.2f}",
            "后续可接入 X、新闻标题、公告、财报电话会文本做真实 NLP 分析",
        ]
        risks: list[str] = []
        if sentiment > 0.78:
            risks.append("市场叙事热度较高，需警惕情绪过热")
        if sentiment < 0.55:
            risks.append("情绪强度一般，缺少明显催化叙事")

        return StrategyScore(name=self.name, score=clamp_score(score), rationale=rationale, risks=risks)
