from app.data_providers.base import DataProvider
from app.models.schemas import Market, StockCandidate


class MockDataProvider(DataProvider):
    """Small mock universe for MVP demos.

    Replace this provider with AKShare/TuShare/yfinance/Polygon in production.
    """

    def get_universe(self, market: Market) -> list[StockCandidate]:
        if market == Market.CN:
            return self._cn_universe()
        return self._us_universe()

    def _us_universe(self) -> list[StockCandidate]:
        return [
            StockCandidate(
                ticker="MSFT",
                name="Microsoft",
                market=Market.US,
                sector="Software / AI Infrastructure",
                price=425.3,
                currency="USD",
                metrics={
                    "pe": 34.2,
                    "roe": 35.1,
                    "revenue_growth": 15.2,
                    "gross_margin": 69.4,
                    "debt_to_equity": 0.32,
                    "six_month_momentum": 18.4,
                    "volatility": 21.3,
                    "news_sentiment": 0.72,
                },
            ),
            StockCandidate(
                ticker="NVDA",
                name="NVIDIA",
                market=Market.US,
                sector="Semiconductors / AI Compute",
                price=910.8,
                currency="USD",
                metrics={
                    "pe": 58.7,
                    "roe": 82.5,
                    "revenue_growth": 126.0,
                    "gross_margin": 74.1,
                    "debt_to_equity": 0.24,
                    "six_month_momentum": 42.6,
                    "volatility": 42.9,
                    "news_sentiment": 0.81,
                },
            ),
            StockCandidate(
                ticker="NOW",
                name="ServiceNow",
                market=Market.US,
                sector="Enterprise Software / Workflow AI",
                price=760.2,
                currency="USD",
                metrics={
                    "pe": 62.4,
                    "roe": 18.3,
                    "revenue_growth": 24.5,
                    "gross_margin": 78.2,
                    "debt_to_equity": 0.44,
                    "six_month_momentum": 16.9,
                    "volatility": 28.4,
                    "news_sentiment": 0.66,
                },
            ),
            StockCandidate(
                ticker="GOOGL",
                name="Alphabet",
                market=Market.US,
                sector="Internet / AI Platform",
                price=172.5,
                currency="USD",
                metrics={
                    "pe": 25.8,
                    "roe": 29.0,
                    "revenue_growth": 13.5,
                    "gross_margin": 56.8,
                    "debt_to_equity": 0.10,
                    "six_month_momentum": 12.1,
                    "volatility": 25.7,
                    "news_sentiment": 0.59,
                },
            ),
            StockCandidate(
                ticker="TSLA",
                name="Tesla",
                market=Market.US,
                sector="EV / Robotics / Energy",
                price=245.1,
                currency="USD",
                metrics={
                    "pe": 72.5,
                    "roe": 12.8,
                    "revenue_growth": 8.7,
                    "gross_margin": 18.3,
                    "debt_to_equity": 0.18,
                    "six_month_momentum": -4.8,
                    "volatility": 55.4,
                    "news_sentiment": 0.48,
                },
            ),
            StockCandidate(
                ticker="LLY",
                name="Eli Lilly",
                market=Market.US,
                sector="Healthcare / GLP-1",
                price=780.6,
                currency="USD",
                metrics={
                    "pe": 51.1,
                    "roe": 58.2,
                    "revenue_growth": 31.0,
                    "gross_margin": 80.5,
                    "debt_to_equity": 1.54,
                    "six_month_momentum": 22.8,
                    "volatility": 29.8,
                    "news_sentiment": 0.74,
                },
            ),
        ]

    def _cn_universe(self) -> list[StockCandidate]:
        return [
            StockCandidate(
                ticker="600519",
                name="贵州茅台",
                market=Market.CN,
                sector="白酒 / 高端消费",
                price=1680.0,
                currency="CNY",
                metrics={
                    "pe": 28.4,
                    "roe": 31.7,
                    "revenue_growth": 17.2,
                    "gross_margin": 91.3,
                    "debt_to_equity": 0.08,
                    "six_month_momentum": 6.2,
                    "volatility": 18.5,
                    "news_sentiment": 0.61,
                },
            ),
            StockCandidate(
                ticker="300750",
                name="宁德时代",
                market=Market.CN,
                sector="新能源 / 动力电池",
                price=196.4,
                currency="CNY",
                metrics={
                    "pe": 21.8,
                    "roe": 24.4,
                    "revenue_growth": 22.0,
                    "gross_margin": 22.8,
                    "debt_to_equity": 0.67,
                    "six_month_momentum": 14.5,
                    "volatility": 36.1,
                    "news_sentiment": 0.64,
                },
            ),
            StockCandidate(
                ticker="688981",
                name="中芯国际",
                market=Market.CN,
                sector="半导体 / 晶圆代工",
                price=52.3,
                currency="CNY",
                metrics={
                    "pe": 68.0,
                    "roe": 4.9,
                    "revenue_growth": 12.4,
                    "gross_margin": 20.1,
                    "debt_to_equity": 0.29,
                    "six_month_momentum": 24.2,
                    "volatility": 44.6,
                    "news_sentiment": 0.67,
                },
            ),
            StockCandidate(
                ticker="000333",
                name="美的集团",
                market=Market.CN,
                sector="家电 / 全球制造",
                price=68.1,
                currency="CNY",
                metrics={
                    "pe": 14.2,
                    "roe": 22.6,
                    "revenue_growth": 9.8,
                    "gross_margin": 26.4,
                    "debt_to_equity": 0.35,
                    "six_month_momentum": 10.1,
                    "volatility": 20.8,
                    "news_sentiment": 0.58,
                },
            ),
            StockCandidate(
                ticker="601318",
                name="中国平安",
                market=Market.CN,
                sector="保险 / 金融",
                price=42.8,
                currency="CNY",
                metrics={
                    "pe": 8.7,
                    "roe": 11.5,
                    "revenue_growth": 4.5,
                    "gross_margin": 0.0,
                    "debt_to_equity": 0.79,
                    "six_month_momentum": 3.7,
                    "volatility": 23.2,
                    "news_sentiment": 0.52,
                },
            ),
        ]
