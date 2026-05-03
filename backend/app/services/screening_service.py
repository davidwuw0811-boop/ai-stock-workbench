from collections import defaultdict

from app.core.disclaimers import RESEARCH_DISCLAIMER
from app.data_providers.mock_provider import MockDataProvider
from app.models.schemas import ScreeningRequest, ScreeningResponse, ScreeningResult, StrategyScore
from app.risk_engine.risk_scoring import build_risk_notes, suitability_text
from app.strategies.registry import STRATEGY_REGISTRY


class ScreeningService:
    def __init__(self) -> None:
        self.data_provider = MockDataProvider()

    def screen(self, request: ScreeningRequest) -> ScreeningResponse:
        candidates = self.data_provider.get_universe(request.market)
        results: list[ScreeningResult] = []

        for candidate in candidates:
            strategy_outputs: list[StrategyScore] = []
            for strategy_name in request.strategies:
                strategy = STRATEGY_REGISTRY[strategy_name]
                strategy_outputs.append(strategy.score(candidate, request.risk_profile))

            if not strategy_outputs:
                continue

            strategy_scores = {output.name: output.score for output in strategy_outputs}
            overall_score = round(sum(strategy_scores.values()) / len(strategy_scores), 2)

            thesis: list[str] = []
            risks: list[str] = []
            seen_thesis: defaultdict[str, bool] = defaultdict(bool)
            seen_risks: defaultdict[str, bool] = defaultdict(bool)

            for output in strategy_outputs:
                for item in output.rationale:
                    if not seen_thesis[item]:
                        thesis.append(item)
                        seen_thesis[item] = True
                for item in output.risks:
                    if not seen_risks[item]:
                        risks.append(item)
                        seen_risks[item] = True

            for item in build_risk_notes(candidate, request.risk_profile):
                if not seen_risks[item]:
                    risks.append(item)
                    seen_risks[item] = True

            results.append(
                ScreeningResult(
                    ticker=candidate.ticker,
                    name=candidate.name,
                    market=candidate.market,
                    sector=candidate.sector,
                    price=candidate.price,
                    currency=candidate.currency,
                    overall_score=overall_score,
                    strategy_scores=strategy_scores,
                    thesis=thesis[:8],
                    risks=risks[:8],
                    suitability=suitability_text(candidate, request.risk_profile, overall_score),
                )
            )

        sorted_results = sorted(results, key=lambda item: item.overall_score, reverse=True)[: request.top_n]
        return ScreeningResponse(
            market=request.market,
            risk_profile=request.risk_profile,
            results=sorted_results,
            disclaimer=RESEARCH_DISCLAIMER,
        )
