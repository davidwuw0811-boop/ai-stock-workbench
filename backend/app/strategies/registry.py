from app.strategies.finrl_adapter import FinRLAdapterStrategy
from app.strategies.fundamental_strategy import FundamentalStrategy
from app.strategies.llm_agent_strategy import LLMAgentStrategy
from app.strategies.momentum_strategy import MomentumStrategy
from app.strategies.sentiment_strategy import SentimentStrategy

STRATEGY_REGISTRY = {
    "fundamental": FundamentalStrategy(),
    "momentum": MomentumStrategy(),
    "sentiment": SentimentStrategy(),
    "finrl": FinRLAdapterStrategy(),
    "llm_agent": LLMAgentStrategy(),
}
