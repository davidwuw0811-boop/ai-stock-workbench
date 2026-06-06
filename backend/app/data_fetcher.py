"""
Data fetcher module: yfinance for both A-shares and US stocks.
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


def _get_cached(key: str) -> Optional[Dict]:
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["data"]
    return None


def _set_cache(key: str, data: Dict):
    _cache[key] = {"data": data, "ts": time.time()}


# ---------------------------------------------------------------------------
# Market detection
# ---------------------------------------------------------------------------
def detect_market(code: str) -> str:
    """Return 'A' for A-shares, 'US' for US stocks."""
    code = code.strip().upper()
    # Pure digits or digits with .SH/.SZ/.SS suffix → A-share
    clean = re.sub(r"\.(SH|SZ|SS|BJ)$", "", code, flags=re.IGNORECASE)
    if clean.isdigit():
        return "A"
    return "US"


def normalize_a_code(code: str) -> str:
    """Normalize A-share code to 6-digit string."""
    clean = re.sub(r"\.(SH|SZ|SS|BJ)$", "", code.strip(), flags=re.IGNORECASE)
    return clean.zfill(6)


def a_code_to_yfinance(code6: str) -> str:
    """Convert 6-digit A-share code to yfinance ticker format.
    
    Rules:
    - 600xxx, 601xxx, 603xxx, 605xxx, 688xxx → .SS (Shanghai)
    - 000xxx, 001xxx, 002xxx, 003xxx, 300xxx, 301xxx → .SZ (Shenzhen)
    - 8xxxxx, 4xxxxx → .BJ (Beijing, not well supported)
    """
    if code6.startswith(('600', '601', '603', '605', '688')):
        return f"{code6}.SS"
    elif code6.startswith(('000', '001', '002', '003', '300', '301')):
        return f"{code6}.SZ"
    elif code6.startswith(('8', '4')):
        return f"{code6}.BJ"
    else:
        # Default to Shanghai
        return f"{code6}.SS"


# ---------------------------------------------------------------------------
# Get Chinese stock name from Tencent API
# ---------------------------------------------------------------------------
def _get_chinese_name(code6: str) -> str:
    """Fetch Chinese stock name from Tencent finance API."""
    import urllib.request
    try:
        # Determine sh/sz prefix
        if code6.startswith(('600', '601', '603', '605', '688')):
            prefix = 'sh'
        else:
            prefix = 'sz'
        url = f"http://qt.gtimg.cn/q={prefix}{code6}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()
            # Try GBK decode
            try:
                text = raw.decode('gbk')
            except Exception:
                text = raw.decode('utf-8', errors='ignore')
            # Parse: format is v_shXXXXXX="1~名称~..."
            parts = text.split('~')
            if len(parts) >= 2 and parts[1]:
                return parts[1]
    except Exception as e:
        logger.warning(f"Failed to get Chinese name for {code6}: {e}")
    return ""


# ---------------------------------------------------------------------------
# A-share data via yfinance (using .SS/.SZ suffix)
# ---------------------------------------------------------------------------
def fetch_a_share(code: str) -> Dict[str, Any]:
    """Fetch A-share financial data using yfinance."""
    import yfinance as yf

    code6 = normalize_a_code(code)
    cache_key = f"A_{code6}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    yf_ticker = a_code_to_yfinance(code6)
    logger.info(f"Fetching A-share {code6} as yfinance ticker: {yf_ticker}")

    # Get Chinese name first
    cn_name = _get_chinese_name(code6)

    result: Dict[str, Any] = {
        "stock_code": code6,
        "stock_name": cn_name or "",
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

    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info or {}

        # Chinese name takes priority over yfinance English/pinyin name
        if not cn_name:
            result["stock_name"] = info.get("shortName") or info.get("longName") or code6
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

        # R&D ratio
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
            hist = stock.history(period="5d")
            if hist is not None and len(hist) >= 2:
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                if prev > 0:
                    result["price_change_pct"] = round((curr - prev) / prev * 100, 2)
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"yfinance error for A-share {yf_ticker}: {e}")

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


# ==================== 新增：财务报表获取功能（供 Piotroski 和多因子使用） ====================

import yfinance as yf
from typing import Dict, Any, Optional
import pandas as pd


def convert_a_share_ticker(stock_code: str) -> str:
    """将 A 股代码转换为 yfinance 可识别的格式"""
    code = str(stock_code).strip()
    if code.startswith(('6', '5')):
        return f"{code}.SS"      # 上海
    elif code.startswith(('0', '3')):
        return f"{code}.SZ"      # 深圳
    else:
        return code              # 美股或其他


def fetch_financial_statements(stock_code: str) -> Dict[str, Any]:
    """
    获取股票的三大财务报表（Income Statement, Balance Sheet, Cash Flow）
    返回结构化数据，方便 Piotroski 和后续多因子计算使用
    """
    ticker = convert_a_share_ticker(stock_code)
    
    try:
        stock = yf.Ticker(ticker)
        
        # 获取三大报表
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cash_flow
        
        if income_stmt.empty:
            return {"error": f"无法获取 {ticker} 的财务数据，可能是 yfinance 数据缺失"}
        
        # 取最近两个报告期（用于同比计算）
        latest_income = income_stmt.iloc[:, 0].to_dict() if not income_stmt.empty else {}
        prev_income = income_stmt.iloc[:, 1].to_dict() if income_stmt.shape[1] > 1 else {}
        
        latest_bs = balance_sheet.iloc[:, 0].to_dict() if not balance_sheet.empty else {}
        prev_bs = balance_sheet.iloc[:, 1].to_dict() if balance_sheet.shape[1] > 1 else {}
        
        latest_cf = cash_flow.iloc[:, 0].to_dict() if not cash_flow.empty else {}
        
        return {
            "ticker": ticker,
            "latest_income": latest_income,
            "previous_income": prev_income,
            "latest_balance_sheet": latest_bs,
            "previous_balance_sheet": prev_bs,
            "latest_cash_flow": latest_cf,
            "data_source": "yfinance",
            "update_time": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"获取财务报表失败: {str(e)}", "ticker": ticker}


def get_piotroski_input_data(stock_code: str) -> Dict[str, Any]:
    """
    专门为 Piotroski F-Score 准备的数据格式
    （可以直接传给 piotroski_scorer.py 使用）
    """
    fin_data = fetch_financial_statements(stock_code)
    
    if "error" in fin_data:
        return fin_data
    
    latest_income = fin_data.get("latest_income", {})
    prev_income = fin_data.get("previous_income", {})
    latest_bs = fin_data.get("latest_balance_sheet", {})
    prev_bs = fin_data.get("previous_balance_sheet", {})
    latest_cf = fin_data.get("latest_cash_flow", {})
    
    return {
        "net_income": latest_income.get("Net Income", 0) or 0,
        "total_assets": latest_bs.get("Total Assets", 0) or 0,
        "operating_cash_flow": latest_cf.get("Operating Cash Flow", 0) or 0,
        "long_term_debt": latest_bs.get("Long Term Debt", 0) or 0,
        "current_assets": latest_bs.get("Current Assets", 0) or 0,
        "current_liabilities": latest_bs.get("Current Liabilities", 0) or 0,
        "gross_profit": latest_income.get("Gross Profit", 0) or 0,
        "total_revenue": latest_income.get("Total Revenue", 0) or 0,
        "previous_total_assets": prev_bs.get("Total Assets", 0) or 0,
        "previous_gross_profit": prev_income.get("Gross Profit", 0) or 0,
        "previous_total_revenue": prev_income.get("Total Revenue", 0) or 0,
    }
