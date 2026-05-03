from app.data_providers.base import DataProvider
from app.data_providers.mock_provider import MockDataProvider
from app.models.schemas import Market, StockCandidate


class YahooProvider(DataProvider):
    """Placeholder for a future yfinance/Polygon/Alpha Vantage provider.

    The MVP intentionally falls back to mock data so the project can run without API keys.
    """

    def __init__(self) -> None:
        self._fallback = MockDataProvider()

    def get_universe(self, market: Market) -> list[StockCandidate]:
        return self._fallback.get_universe(market)
