from abc import ABC, abstractmethod

from app.models.schemas import Market, StockCandidate


class DataProvider(ABC):
    @abstractmethod
    def get_universe(self, market: Market) -> list[StockCandidate]:
        """Return a candidate universe for a market."""
