"""
Data fetcher module: AKShare for A-shares, yfinance for US stocks.
Includes in-memory cache with 30-minute TTL.
"""

import time
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Simple in-memory cache
# ---------------------------------------------------------------------------
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 1800  # 30 minutes

# Global cache for the full A-share spot table (very large, fetched once)
_a_spot_cache: Dict[str, Any] = {"data": None, "ts": 0}
A_SPOT_TTL = 600  # 10 minutes


def _get_cached(key: str) -> Optional[Dict]:
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["data"]
    return None


def _set_cache(key: str, data: Dict):
    _cache[key] = {"data": data, "ts": time.time()}


def _get_a_spot_table():
    """Get the full A-share spot table, cached for 10 minutes."""
    import akshare as ak
    if _a_spot_cache["data"] is not None and time.time() - _a_spot_cache["ts"] < A_SPOT_TTL:
        return _a_spot_cache["data"]
    try:
        df = ak.stock_zh_a_spot_em()
        _a_spot_cache["data"] = df
        _a_spot_cache["ts"] = time.time()
        return df
    except Exception as e:
        logger.warning(f"Failed to fetch A-share spot table: {e}")
        return _a_spot_cache.get("data")  # Return stale data if available


# ---------------------------------------------------------------------------
# Market detection
# ---------------------------------------------------------------------------
def detect_market(code: str) -> str:
    """Return 'A' for A-shares, 'US' for US stocks."""
    code = code.strip().upper()
    # Pure digits or digits with .SH/.SZ suffix → A-share
    clean = re.sub(r"\.(SH|SZ|BJ)$", "", code, flags=re.IGNORECASE)
    if clean.isdigit():
        return "A"
    return "US"


def normalize_a_code(code: str) -> str:
    """Normalize A-share code to 6-digit string."""
    clean = re.sub(r"\.(SH|SZ|BJ)$", "", code.strip(), flags=re.IGNORECASE)
    return clean.zfill(6)


# ---------------------------------------------------------------------------
# A-share data via AKShare
# ---------------------------------------------------------------------------
def fetch_a_share(code: str) -> Dict[str, Any]:
    """Fetch A-share financial data using AKShare."""
    import akshare as ak

    code6 = normalize_a_code(code)
    cache_key = f"A_{code6}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    result: Dict[str, Any] = {
        "stock_code": code6,
        "stock_name": "",
        "market": "A股",
        "current_price": None,
        "pe": None,
        "roe": None,
        "debt_ratio": None,
        "revenue_growth": None,
        "net_profit_growth": None,
        "peg": None,
        "gross_margin": None,
        "market_cap": None,
        "free_cash_flow": None,
        "rd_ratio": None,
        "price_change_pct": None,
        "industry": "",
        "pb": None,
        "dividend_yield": None,
    }

    # 1) Real-time quote via cached spot table
    try:
        df_spot = _get_a_spot_table()
        row = df_spot[df_spot["代码"] == code6] if df_spot is not None else None
        if row is not None and not row.empty:
            r = row.iloc[0]
            result["stock_name"] = str(r.get("名称", ""))
            result["current_price"] = _safe_float(r.get("最新价"))
            result["pe"] = _safe_float(r.get("市盈率-动态"))
            result["pb"] = _safe_float(r.get("市净率"))
            result["market_cap"] = _safe_float(r.get("总市值"))
            result["price_change_pct"] = _safe_float(r.get("涨跌幅"))
    except Exception as e:
        logger.warning(f"AKShare spot data error for {code6}: {e}")

    # 2) Financial indicators via ak.stock_financial_abstract_ths()
    try:
        df_fin = ak.stock_financial_abstract_ths(symbol=code6, indicator="按年度")
        if df_fin is not None and not df_fin.empty:
            latest = df_fin.iloc[0]
            result["roe"] = _safe_float(latest.get("净资产收益率"))
            result["revenue_growth"] = _safe_float(latest.get("营业总收入同比增长率"))
            result["net_profit_growth"] = _safe_float(latest.get("净利润同比增长率"))
            result["gross_margin"] = _safe_float(latest.get("销售毛利率"))
            result["debt_ratio"] = _safe_float(latest.get("资产负债率"))
    except Exception as e:
        logger.warning(f"AKShare financial abstract error for {code6}: {e}")

    # 3) Try individual indicators if still missing
    try:
        if result["roe"] is None:
            df_roe = ak.stock_financial_analysis_indicator(symbol=code6)
            if df_roe is not None and not df_roe.empty:
                latest = df_roe.iloc[0]
                result["roe"] = _safe_float(latest.get("净资产收益率(%)"))
                if result["gross_margin"] is None:
                    result["gross_margin"] = _safe_float(latest.get("销售毛利率(%)"))
    except Exception as e:
        logger.warning(f"AKShare indicator error for {code6}: {e}")

    # 4) Calculate PEG if possible
    if result["pe"] and result["net_profit_growth"] and result["net_profit_growth"] > 0:
        result["peg"] = round(result["pe"] / result["net_profit_growth"], 2)

    # 5) Industry info
    try:
        df_info = ak.stock_individual_info_em(symbol=code6)
        if df_info is not None and not df_info.empty:
            ind_row = df_info[df_info["item"] == "行业"]
            if not ind_row.empty:
                result["industry"] = str(ind_row.iloc[0]["value"])
    except Exception as e:
        logger.warning(f"AKShare industry info error for {code6}: {e}")

    _set_cache(cache_key, result)
    return result


# ---------------------------------------------------------------------------
# US stock data via yfinance
# ---------------------------------------------------------------------------
def fetch_us_stock(ticker: str) -> Dict[str, Any]:
    """Fetch US stock financial data using yfinance."""
    import yfinance as yf

    ticker = ticker.strip().upper()
    cache_key = f"US_{ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    result: Dict[str, Any] = {
        "stock_code": ticker,
        "stock_name": "",
        "market": "美股",
        "current_price": None,
        "pe": None,
        "roe": None,
        "debt_ratio": None,
        "revenue_growth": None,
        "net_profit_growth": None,
        "peg": None,
        "gross_margin": None,
        "market_cap": None,
        "free_cash_flow": None,
        "rd_ratio": None,
        "price_change_pct": None,
        "industry": "",
        "pb": None,
        "dividend_yield": None,
    }

    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        result["stock_name"] = info.get("shortName") or info.get("longName") or ticker
        result["current_price"] = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
        result["pe"] = _safe_float(info.get("trailingPE") or info.get("forwardPE"))
        result["pb"] = _safe_float(info.get("priceToBook"))
        result["peg"] = _safe_float(info.get("pegRatio"))
        result["market_cap"] = _safe_float(info.get("marketCap"))
        result["dividend_yield"] = _safe_float(info.get("dividendYield"))
        result["industry"] = info.get("industry") or info.get("sector") or ""
        result["gross_margin"] = _pct(info.get("grossMargins"))
        result["roe"] = _pct(info.get("returnOnEquity"))
        result["revenue_growth"] = _pct(info.get("revenueGrowth"))
        result["net_profit_growth"] = _pct(info.get("earningsGrowth") or info.get("earningsQuarterlyGrowth"))
        result["free_cash_flow"] = _safe_float(info.get("freeCashflow"))

        # Debt ratio
        total_debt = _safe_float(info.get("totalDebt"))
        total_assets = _safe_float(info.get("totalAssets"))
        if total_debt and total_assets and total_assets > 0:
            result["debt_ratio"] = round(total_debt / total_assets * 100, 2)

        # R&D ratio (from financials)
        try:
            financials = stock.financials
            if financials is not None and not financials.empty:
                rd_row = None
                for label in ["Research Development", "ResearchAndDevelopmentExpense", "Research And Development"]:
                    if label in financials.index:
                        rd_row = financials.loc[label]
                        break
                rev_row = None
                for label in ["Total Revenue", "TotalRevenue"]:
                    if label in financials.index:
                        rev_row = financials.loc[label]
                        break
                if rd_row is not None and rev_row is not None:
                    rd_val = _safe_float(rd_row.iloc[0])
                    rev_val = _safe_float(rev_row.iloc[0])
                    if rd_val and rev_val and rev_val > 0:
                        result["rd_ratio"] = round(rd_val / rev_val * 100, 2)
        except Exception:
            pass

        # Price change
        try:
            hist = stock.history(period="2d")
            if hist is not None and len(hist) >= 2:
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                if prev > 0:
                    result["price_change_pct"] = round((curr - prev) / prev * 100, 2)
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"yfinance error for {ticker}: {e}")

    _set_cache(cache_key, result)
    return result


# ---------------------------------------------------------------------------
# Unified fetch
# ---------------------------------------------------------------------------
def fetch_stock(code: str) -> Dict[str, Any]:
    """Auto-detect market and fetch data."""
    market = detect_market(code)
    if market == "A":
        return fetch_a_share(code)
    else:
        return fetch_us_stock(code)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        if f != f:  # NaN check
            return None
        return round(f, 4)
    except (ValueError, TypeError):
        return None


def _pct(val) -> Optional[float]:
    """Convert ratio (0.25) to percentage (25.0)."""
    f = _safe_float(val)
    if f is not None:
        return round(f * 100, 2)
    return None
