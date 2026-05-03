"""
AI Stock Workbench — FastAPI Backend
Real-time stock analysis with three investor style scoring models.
"""

import logging
import traceback
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .data_fetcher import fetch_stock, detect_market
from .scoring import score_buffett, score_ark, score_lynch, generate_strategy_signals, generate_conclusion

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Stock Workbench API",
    description="投资大师风格引擎 — 实时股票分析API。本工具仅供投研参考，不构成任何投资建议。",
    version="1.0.0",
)

# CORS — allow all origins for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Common stock search database (for fuzzy matching)
# ---------------------------------------------------------------------------
STOCK_DB = [
    # A-shares
    {"code": "600519", "name": "贵州茅台", "market": "A股"},
    {"code": "300750", "name": "宁德时代", "market": "A股"},
    {"code": "002594", "name": "比亚迪", "market": "A股"},
    {"code": "601318", "name": "中国平安", "market": "A股"},
    {"code": "600036", "name": "招商银行", "market": "A股"},
    {"code": "688981", "name": "中芯国际", "market": "A股"},
    {"code": "601012", "name": "隆基绿能", "market": "A股"},
    {"code": "300760", "name": "迈瑞医疗", "market": "A股"},
    {"code": "600900", "name": "长江电力", "market": "A股"},
    {"code": "000858", "name": "五粮液", "market": "A股"},
    {"code": "000333", "name": "美的集团", "market": "A股"},
    {"code": "600276", "name": "恒瑞医药", "market": "A股"},
    {"code": "002415", "name": "海康威视", "market": "A股"},
    {"code": "601899", "name": "紫金矿业", "market": "A股"},
    {"code": "600809", "name": "山西汾酒", "market": "A股"},
    {"code": "002304", "name": "洋河股份", "market": "A股"},
    {"code": "601888", "name": "中国中免", "market": "A股"},
    {"code": "000001", "name": "平安银行", "market": "A股"},
    {"code": "600030", "name": "中信证券", "market": "A股"},
    {"code": "603259", "name": "药明康德", "market": "A股"},
    # US stocks
    {"code": "AAPL", "name": "Apple", "market": "美股"},
    {"code": "NVDA", "name": "NVIDIA", "market": "美股"},
    {"code": "MSFT", "name": "Microsoft", "market": "美股"},
    {"code": "GOOGL", "name": "Alphabet (Google)", "market": "美股"},
    {"code": "TSLA", "name": "Tesla", "market": "美股"},
    {"code": "AMZN", "name": "Amazon", "market": "美股"},
    {"code": "META", "name": "Meta Platforms", "market": "美股"},
    {"code": "BRK-B", "name": "Berkshire Hathaway", "market": "美股"},
    {"code": "PLTR", "name": "Palantir", "market": "美股"},
    {"code": "AMD", "name": "AMD", "market": "美股"},
    {"code": "NFLX", "name": "Netflix", "market": "美股"},
    {"code": "CRM", "name": "Salesforce", "market": "美股"},
    {"code": "BABA", "name": "Alibaba", "market": "美股"},
    {"code": "TSM", "name": "TSMC", "market": "美股"},
    {"code": "COIN", "name": "Coinbase", "market": "美股"},
    {"code": "SNOW", "name": "Snowflake", "market": "美股"},
    {"code": "SQ", "name": "Block (Square)", "market": "美股"},
    {"code": "SHOP", "name": "Shopify", "market": "美股"},
    {"code": "UBER", "name": "Uber", "market": "美股"},
    {"code": "ABNB", "name": "Airbnb", "market": "美股"},
]

DISCLAIMER = "免责声明：本模型只是将公开投资理念转化为量化筛选因子，用于研究和教育，不代表巴菲特、芒格、Cathie Wood 或 ARK 的真实投资意见，也不构成任何投资建议。投资有风险，入市需谨慎。"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI Stock Workbench API", "version": "1.0.0"}


@app.get("/api/search")
async def search_stocks(q: str = Query(..., min_length=1, description="搜索关键词")):
    """Fuzzy search stocks by code or name."""
    q_upper = q.strip().upper()
    q_lower = q.strip().lower()
    results = []
    for s in STOCK_DB:
        if (q_upper in s["code"].upper()
            or q_lower in s["name"].lower()
            or q_upper in s["name"].upper()):
            results.append(s)
    return {"query": q, "results": results[:10]}


@app.get("/api/analyze/{stock_code}")
async def analyze_stock(stock_code: str):
    """
    Analyze a stock with all three investor styles and strategy signals.
    Accepts A-share codes (e.g., 600519) or US tickers (e.g., AAPL).
    """
    stock_code = stock_code.strip()
    if not stock_code:
        raise HTTPException(status_code=400, detail="股票代码不能为空")

    try:
        # 1. Fetch data
        logger.info(f"Fetching data for {stock_code}")
        data = fetch_stock(stock_code)

        if not data.get("stock_name") and not data.get("current_price"):
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票 {stock_code} 的数据，请检查代码是否正确"
            )

        # 2. Score with three styles
        buffett = score_buffett(data)
        ark = score_ark(data)
        lynch = score_lynch(data)

        # 3. Strategy signals
        strategies = generate_strategy_signals(data)

        # 4. Conclusion
        conclusion = generate_conclusion(data, buffett, ark, lynch, strategies)

        # 5. Build response
        response = {
            "stock_code": data["stock_code"],
            "stock_name": data["stock_name"],
            "market": data["market"],
            "current_price": data["current_price"],
            "basic_data": {
                "pe": data["pe"],
                "roe": data["roe"],
                "debt_ratio": data["debt_ratio"],
                "revenue_growth": data["revenue_growth"],
                "net_profit_growth": data["net_profit_growth"],
                "peg": data["peg"],
                "gross_margin": data["gross_margin"],
                "market_cap": data["market_cap"],
                "free_cash_flow": data["free_cash_flow"],
                "rd_ratio": data["rd_ratio"],
                "price_change_pct": data["price_change_pct"],
                "industry": data["industry"],
                "pb": data["pb"],
                "dividend_yield": data["dividend_yield"],
            },
            "styles": {
                "buffett": buffett,
                "ark": ark,
                "lynch": lynch,
            },
            "strategies": strategies,
            "conclusion": conclusion,
            "disclaimer": DISCLAIMER,
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {stock_code}: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"分析 {stock_code} 时出错：{str(e)}。请稍后重试。"
        )


@app.get("/")
async def root():
    return {
        "service": "AI Stock Workbench API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "search": "/api/search?q=<keyword>",
            "analyze": "/api/analyze/<stock_code>",
        },
        "disclaimer": DISCLAIMER,
    }
