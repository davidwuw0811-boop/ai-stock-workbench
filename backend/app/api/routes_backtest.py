from fastapi import APIRouter

from app.models.schemas import BacktestRequest, BacktestResponse

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """Mock backtest endpoint.

    Replace this with Backtrader/VectorBT/FinRL backtesting in production.
    """
    strategy_bias = {
        "fundamental": 0.112,
        "momentum": 0.138,
        "sentiment": 0.096,
        "finrl": 0.154,
        "llm_agent": 0.121,
    }.get(request.strategy, 0.1)
    final_value = round(request.initial_cash * (1 + strategy_bias) ** 3, 2)

    return BacktestResponse(
        market=request.market,
        strategy=request.strategy,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_cash=request.initial_cash,
        final_value=final_value,
        annualized_return=round(strategy_bias, 3),
        max_drawdown=round(-0.18 if request.strategy != "finrl" else -0.22, 3),
        sharpe_ratio=round(1.12 if request.strategy != "sentiment" else 0.92, 2),
        win_rate=round(0.56 if request.strategy != "finrl" else 0.58, 2),
        turnover=round(0.42 if request.strategy == "fundamental" else 0.87, 2),
        note="MVP mock result. Connect a real backtesting engine before production use.",
    )
