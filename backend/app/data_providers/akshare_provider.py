from app.data_providers.base import DataProvider
from app.data_providers.mock_provider import MockDataProvider
from app.models.schemas import Market, StockCandidate


class AKShareProvider(DataProvider):
    """Placeholder for AKShare-based China A-share data.

    TODO: install akshare and implement real data loading in production.
    """

    def __init__(self) -> None:
        self._fallback = MockDataProvider()

    def get_universe(self, market: Market) -> list[StockCandidate]:
        return self._fallback.get_universe(market)
