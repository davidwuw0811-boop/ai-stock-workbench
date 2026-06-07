"""
AI Stock Workbench — FastAPI Backend
Real-time stock analysis with three investor style scoring models.
"""

import logging
import traceback
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .data_fetcher import fetch_stock, detect_market, normalize_a_code, a_code_to_yfinance
from .scoring import score_buffett, score_ark, score_lynch, generate_strategy_signals, generate_conclusion
from app.piotroski_scorer import calculate_piotroski_score
from app.data_fetcher import fetch_financial_statements  # 可选，用于调试

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


@app.get("/api/chart/{stock_code}")
async def chart_data(stock_code: str):
    """
    Return recent 60 trading days OHLC data for charting.
    A-shares use Eastmoney API; US stocks use yfinance.
    Accepts A-share codes (e.g., 600519) or US tickers (e.g., AAPL).
    """
    import requests as _requests

    stock_code = stock_code.strip()
    if not stock_code:
        raise HTTPException(status_code=400, detail="股票代码不能为空")
    try:
        market = detect_market(stock_code)

        if market == "A":
            # --- A-share: use Eastmoney push2his API ---
            code6 = normalize_a_code(stock_code)
            # Determine market prefix: 1.=Shanghai, 0.=Shenzhen
            if code6.startswith(('600', '601', '603', '605', '688')):
                secid = f"1.{code6}"
            else:
                secid = f"0.{code6}"

            logger.info(f"Fetching Eastmoney chart data for secid={secid}")
            url = (
                "http://push2his.eastmoney.com/api/qt/stock/kline/get"
                f"?secid={secid}"
                "&fields1=f1,f2,f3,f4,f5,f6"
                "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
                "&klt=101&fqt=1&end=20500101&lmt=60"
            )
            resp = _requests.get(url, timeout=10)
            resp.raise_for_status()
            json_data = resp.json()

            klines = json_data.get("data", {}).get("klines") if json_data.get("data") else None
            if not klines:
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到股票 {stock_code} 的历史数据"
                )

            records = []
            for line in klines:
                # Format: 日期,开盘,收盘,最高,最低,成交量,成交额,...
                parts = line.split(",")
                records.append({
                    "date": parts[0],
                    "open": round(float(parts[1]), 2),
                    "close": round(float(parts[2]), 2),
                    "high": round(float(parts[3]), 2),
                    "low": round(float(parts[4]), 2),
                    "volume": int(float(parts[5])),
                })

            return {
                "stock_code": stock_code,
                "ticker": secid,
                "market": "A股",
                "data": records,
            }

        else:
            # --- US stock: try Eastmoney first (105.=NASDAQ, 106.=NYSE), fallback to yfinance ---
            ticker_upper = stock_code.upper()
            records = None

            for prefix in ["105", "106"]:
                secid = f"{prefix}.{ticker_upper}"
                logger.info(f"Trying Eastmoney US chart: secid={secid}")
                url = (
                    "http://push2his.eastmoney.com/api/qt/stock/kline/get"
                    f"?secid={secid}"
                    "&fields1=f1,f2,f3,f4,f5,f6"
                    "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
                    "&klt=101&fqt=1&end=20500101&lmt=60"
                )
                try:
                    resp = _requests.get(url, timeout=10)
                    resp.raise_for_status()
                    json_data = resp.json()
                    klines = json_data.get("data", {}).get("klines") if json_data.get("data") else None
                    if klines and len(klines) > 0:
                        records = []
                        for line in klines:
                            parts = line.split(",")
                            records.append({
                                "date": parts[0],
                                "open": round(float(parts[1]), 2),
                                "close": round(float(parts[2]), 2),
                                "high": round(float(parts[3]), 2),
                                "low": round(float(parts[4]), 2),
                                "volume": int(float(parts[5])),
                            })
                        return {
                            "stock_code": stock_code,
                            "ticker": secid,
                            "market": "美股",
                            "data": records,
                        }
                except Exception as em_err:
                    logger.warning(f"Eastmoney US {secid} failed: {em_err}")
                    continue

            # Fallback: yfinance for US stocks
            logger.info(f"Falling back to yfinance for {ticker_upper}")
            import yfinance as yf
            ticker = yf.Ticker(ticker_upper)
            hist = ticker.history(period="3mo")
            if hist.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"未找到股票 {stock_code} 的历史数据"
                )
            hist = hist.tail(60)
            records = []
            for idx, row in hist.iterrows():
                records.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                })
            return {
                "stock_code": stock_code,
                "ticker": ticker_upper,
                "market": "美股",
                "data": records,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chart for {stock_code}: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"获取 {stock_code} 图表数据时出错：{str(e)}"
        )


# ==================== Step 5 新增：Piotroski + 扫描接口 ====================

@app.get("/api/analyze_with_piotroski/{stock_code}")
async def analyze_with_piotroski(stock_code: str):
    """单只股票分析 + Piotroski F-Score（测试用）"""
    try:
        # 调用现有分析（保持你原来的逻辑）
        existing_analysis = await analyze_stock(stock_code)
        
        # 计算 Piotroski
        piotroski_result = calculate_piotroski_score(stock_code)
        
        # 合并返回
        return {
            "stock_code": stock_code,
            "existing_styles": existing_analysis,
            "piotroski": piotroski_result,
            "composite_score": round((existing_analysis.get("average_style_score", 0) * 0.7 + piotroski_result["piotroski_score"] * 0.3), 1) if "average_style_score" in existing_analysis else piotroski_result["piotroski_score"],
            "message": "Piotroski F-Score 已集成！"
        }
    except Exception as e:
        return {"error": str(e)}


from pydantic import BaseModel

class ScanRequest(BaseModel):
    """扫描请求模型"""
    tickers: List[str]

@app.post("/api/scan_custom")
async def scan_custom(request: ScanRequest):
    """全市场扫描 - 修复版（支持复合评分）"""
    try:
        tickers = request.tickers
        if not tickers or len(tickers) > 50:
            return {"error": "请提供1-50只股票代码"}
        
        results = []
        for code in tickers:
            # 调用原有风格分析
            try:
                style_result = await analyze_stock(code)
            except:
                style_result = None
            
            piotroski = calculate_piotroski_score(code)
            
            # 从三大风格评分中计算平均分
            if style_result and "styles" in style_result:
                styles = style_result["styles"]
                buffett_score = styles.get("buffett", {}).get("score", 0)
                ark_score = styles.get("ark", {}).get("score", 0)
                lynch_score = styles.get("lynch", {}).get("score", 0)
                style_score = round((buffett_score + ark_score + lynch_score) / 3, 1)
            else:
                style_score = 0
            piotroski_score = piotroski.get("piotroski_score", 0)
            # 把Piotroski 权重提到 60%（更强调财务健康）
            composite = round(style_score * 0.4 + (piotroski_score / 9 * 100) * 0.6, 1)
            
            results.append({
                "stock_code": code,
                "style_score": round(style_score, 1),
                "piotroski_score": piotroski_score,
                "composite_score": composite,
                "interpretation": piotroski.get("interpretation", "无数据"),
                "rank": "⭐ 高潜力" if composite >= 75 else "🟡 中等" if composite >= 60 else "⚪ 观察"
            })
        
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return {
            "scan_time": "just now",
            "total_scanned": len(tickers),
            "top_picks": results[:15],
            "all_results": results
        }
    except Exception as e:
        return {"error": f"扫描失败: {str(e)}"}


@app.get("/api/csi300_tickers")
async def get_csi300_tickers():
    """返回沪深300成分股列表（动态获取）"""
    try:
        import akshare as ak
        df = ak.index_stock_cons_csindex(symbol="000300")  # 真实沪深300成分股
        tickers = df["代码"].tolist()[:100]  # 先取前100只
        return {"tickers": tickers, "total": len(tickers)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def root():
    return {
        "service": "AI Stock Workbench API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "search": "/api/search?q=<keyword>",
            "analyze": "/api/analyze/<stock_code>",
            "chart": "/api/chart/<stock_code>",
            "analyze_with_piotroski": "/api/analyze_with_piotroski/<stock_code>",
            "scan_custom": "/api/scan_custom (POST)",
        },
        "disclaimer": DISCLAIMER,
    }
