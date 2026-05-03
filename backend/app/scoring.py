"""
Three investor style scoring models:
1. Buffett-Munger (Quality Value)
2. Cathie Wood / ARK (Disruptive Innovation Growth)
3. Peter Lynch (Growth at Reasonable Price)

Plus strategy signal generators.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Innovation industry keywords
# ---------------------------------------------------------------------------
INNOVATION_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "semiconductor", "chip",
    "autonomous", "self-driving", "robotics", "robot", "biotech", "genomics",
    "gene", "crispr", "electric vehicle", "ev", "battery", "solar", "renewable",
    "blockchain", "crypto", "fintech", "saas", "cloud", "quantum", "space",
    "3d print", "drone", "vr", "ar", "metaverse",
    "人工智能", "芯片", "半导体", "新能源", "电池", "光伏", "自动驾驶",
    "机器人", "生物科技", "基因", "创新药", "云计算", "大数据", "区块链",
    "量子", "无人机", "储能", "氢能", "智能制造",
]


def _clamp(val: float, lo: float = 0, hi: float = 100) -> float:
    return max(lo, min(hi, val))


def _score_linear(val: Optional[float], low: float, high: float) -> float:
    """Linear score: val at low→0, val at high→100."""
    if val is None:
        return 50  # neutral default
    if high == low:
        return 50
    return _clamp((val - low) / (high - low) * 100)


def _score_inverse(val: Optional[float], low: float, high: float) -> float:
    """Inverse linear: val at low→100, val at high→0."""
    if val is None:
        return 50
    return _clamp(100 - (val - low) / (high - low) * 100)


def _is_innovation_industry(industry: str) -> bool:
    industry_lower = industry.lower()
    return any(kw in industry_lower for kw in INNOVATION_KEYWORDS)


# ===================================================================
# 1. Buffett-Munger: Quality Value
# ===================================================================
def score_buffett(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dimensions (weights):
    - ROE (20%): >15% good, >25% excellent
    - Debt ratio (15%): <50% good, <30% excellent
    - Earnings stability / net profit growth (15%): positive and stable
    - Free cash flow (15%): positive is good
    - Moat / gross margin (15%): >40% strong moat
    - Valuation / PE (15%): reasonable PE
    - Management / dividend (5%): dividend yield as proxy
    """
    dims = {}

    # ROE score (0-100)
    roe = data.get("roe")
    dims["ROE质量"] = round(_score_linear(roe, 0, 35))

    # Debt ratio (lower is better)
    debt = data.get("debt_ratio")
    dims["负债水平"] = round(_score_inverse(debt, 0, 80))

    # Earnings stability (net profit growth positive is good)
    npg = data.get("net_profit_growth")
    if npg is not None:
        if npg > 0:
            dims["盈利稳定性"] = round(_clamp(60 + npg * 1.5, 0, 100))
        else:
            dims["盈利稳定性"] = round(_clamp(60 + npg * 2, 0, 100))
    else:
        dims["盈利稳定性"] = 50

    # Free cash flow
    fcf = data.get("free_cash_flow")
    if fcf is not None:
        if fcf > 0:
            dims["自由现金流"] = round(_clamp(70 + min(fcf / 1e9, 30), 0, 100))
        else:
            dims["自由现金流"] = round(_clamp(30 + fcf / 1e9, 0, 100))
    else:
        dims["自由现金流"] = 50

    # Moat (gross margin)
    gm = data.get("gross_margin")
    dims["护城河"] = round(_score_linear(gm, 10, 70))

    # Valuation (PE: 5-25 ideal range)
    pe = data.get("pe")
    if pe is not None and pe > 0:
        if pe <= 15:
            dims["估值合理性"] = 95
        elif pe <= 25:
            dims["估值合理性"] = round(95 - (pe - 15) * 3)
        elif pe <= 50:
            dims["估值合理性"] = round(65 - (pe - 25) * 1.5)
        else:
            dims["估值合理性"] = round(max(10, 30 - (pe - 50) * 0.5))
    else:
        dims["估值合理性"] = 50

    # Management (dividend yield as proxy)
    dy = data.get("dividend_yield")
    if dy is not None:
        dims["管理层质量"] = round(_clamp(50 + dy * 100 * 5, 0, 100))
    else:
        dims["管理层质量"] = 50

    # Weighted total
    weights = {
        "ROE质量": 0.20, "负债水平": 0.15, "盈利稳定性": 0.15,
        "自由现金流": 0.15, "护城河": 0.15, "估值合理性": 0.15,
        "管理层质量": 0.05,
    }
    total = sum(dims[k] * weights[k] for k in weights)
    total = round(_clamp(total, 0, 100))

    # Generate summary
    summary = _buffett_summary(data, dims, total)

    return {"score": total, "dimensions": dims, "summary": summary}


def _buffett_summary(data: Dict, dims: Dict, score: int) -> str:
    name = data.get("stock_name", data.get("stock_code", ""))
    parts = []
    if dims["ROE质量"] >= 70:
        parts.append(f"ROE表现优秀({data.get('roe', 'N/A')}%)")
    if dims["负债水平"] >= 70:
        parts.append("负债率健康")
    if dims["护城河"] >= 70:
        parts.append(f"毛利率{data.get('gross_margin', 'N/A')}%显示较强护城河")
    if dims["自由现金流"] >= 70:
        parts.append("自由现金流充沛")
    if dims["估值合理性"] >= 70:
        parts.append("估值合理")

    risks = []
    if dims["估值合理性"] < 50:
        risks.append("估值偏高")
    if dims["负债水平"] < 50:
        risks.append("负债率偏高")
    if dims["ROE质量"] < 50:
        risks.append("ROE偏低")

    if score >= 80:
        prefix = f"{name}高度符合巴菲特-芒格式质量价值筛选。"
    elif score >= 60:
        prefix = f"{name}较好符合巴菲特-芒格式质量价值框架。"
    elif score >= 40:
        prefix = f"{name}部分符合巴菲特-芒格式价值标准。"
    else:
        prefix = f"{name}不太符合巴菲特-芒格式价值投资标准。"

    strengths = "、".join(parts) if parts else "暂无突出亮点"
    risk_str = "、".join(risks) if risks else "风险可控"
    return f"{prefix}优势：{strengths}。风险提示：{risk_str}。"


# ===================================================================
# 2. Cathie Wood / ARK: Disruptive Innovation Growth
# ===================================================================
def score_ark(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dimensions (weights):
    - Theme fit (25%): is it in innovation sector?
    - Revenue growth (20%): >25% is good
    - R&D intensity (15%): higher is better
    - Platform potential (15%): market cap vs potential
    - Market space (15%): based on industry + growth
    - Valuation risk (-10%): penalty for extreme PE
    """
    dims = {}

    # Theme fit
    industry = data.get("industry", "")
    if _is_innovation_industry(industry):
        dims["主题契合度"] = 90
    else:
        # Partial credit for high-growth companies
        rg = data.get("revenue_growth")
        if rg and rg > 30:
            dims["主题契合度"] = 60
        elif rg and rg > 15:
            dims["主题契合度"] = 40
        else:
            dims["主题契合度"] = 20

    # Revenue growth
    rg = data.get("revenue_growth")
    if rg is not None:
        if rg > 50:
            dims["收入增长"] = 98
        elif rg > 25:
            dims["收入增长"] = round(70 + (rg - 25) * 1.12)
        elif rg > 0:
            dims["收入增长"] = round(30 + rg * 1.6)
        else:
            dims["收入增长"] = round(max(5, 30 + rg))
    else:
        dims["收入增长"] = 40

    # R&D intensity
    rd = data.get("rd_ratio")
    if rd is not None:
        dims["研发强度"] = round(_score_linear(rd, 0, 25))
    else:
        # If no R&D data, use industry as proxy
        if _is_innovation_industry(industry):
            dims["研发强度"] = 65
        else:
            dims["研发强度"] = 35

    # Platform potential (inverse of market cap — smaller = more upside)
    mc = data.get("market_cap")
    if mc is not None:
        if mc < 10e9:
            dims["平台潜力"] = 90
        elif mc < 50e9:
            dims["平台潜力"] = 75
        elif mc < 200e9:
            dims["平台潜力"] = 60
        elif mc < 1e12:
            dims["平台潜力"] = 45
        else:
            dims["平台潜力"] = 30
    else:
        dims["平台潜力"] = 50

    # Market space
    if _is_innovation_industry(industry):
        base = 75
    else:
        base = 40
    rg_bonus = min(20, max(0, (data.get("revenue_growth") or 0) * 0.5))
    dims["市场空间"] = round(_clamp(base + rg_bonus, 0, 100))

    # Valuation risk (penalty)
    pe = data.get("pe")
    if pe is not None and pe > 0:
        if pe > 200:
            dims["估值风险"] = -15
        elif pe > 100:
            dims["估值风险"] = -10
        elif pe > 60:
            dims["估值风险"] = -5
        else:
            dims["估值风险"] = 0
    else:
        dims["估值风险"] = -5

    # Weighted total
    weights = {
        "主题契合度": 0.25, "收入增长": 0.20, "研发强度": 0.15,
        "平台潜力": 0.15, "市场空间": 0.15,
    }
    total = sum(dims[k] * weights[k] for k in weights) + dims["估值风险"]
    total = round(_clamp(total, 0, 100))

    summary = _ark_summary(data, dims, total)
    return {"score": total, "dimensions": dims, "summary": summary}


def _ark_summary(data: Dict, dims: Dict, score: int) -> str:
    name = data.get("stock_name", data.get("stock_code", ""))
    parts = []
    if dims["主题契合度"] >= 70:
        parts.append(f"行业({data.get('industry', '未知')})高度契合创新主题")
    if dims["收入增长"] >= 70:
        parts.append(f"营收增长强劲({data.get('revenue_growth', 'N/A')}%)")
    if dims["研发强度"] >= 60:
        parts.append("研发投入力度大")
    if dims["平台潜力"] >= 70:
        parts.append("平台化潜力显著")

    risks = []
    if dims["估值风险"] < -5:
        risks.append("估值极高")
    if dims["主题契合度"] < 50:
        risks.append("非典型创新赛道")
    if dims["收入增长"] < 40:
        risks.append("增长动力不足")

    if score >= 80:
        prefix = f"{name}极度契合ARK颠覆式创新成长框架。"
    elif score >= 60:
        prefix = f"{name}较好契合ARK颠覆式创新框架。"
    elif score >= 40:
        prefix = f"{name}部分符合ARK创新投资理念。"
    else:
        prefix = f"{name}不太符合ARK颠覆式创新标准。"

    strengths = "、".join(parts) if parts else "创新属性有限"
    risk_str = "、".join(risks) if risks else "风险可控"
    return f"{prefix}优势：{strengths}。风险提示：{risk_str}。"


# ===================================================================
# 3. Peter Lynch: Growth at Reasonable Price (GARP)
# ===================================================================
def score_lynch(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dimensions (weights):
    - PEG reasonableness (25%): <1 excellent, <1.5 good
    - Earnings growth (20%): >15% is good
    - Business understandability (15%): proxy via industry
    - Financial health (15%): debt ratio + ROE
    - Growth space (15%): market cap + growth
    - Valuation (10%): PE level
    """
    dims = {}

    # PEG
    peg = data.get("peg")
    if peg is not None and peg > 0:
        if peg <= 0.5:
            dims["PEG合理性"] = 98
        elif peg <= 1.0:
            dims["PEG合理性"] = round(80 + (1.0 - peg) * 36)
        elif peg <= 1.5:
            dims["PEG合理性"] = round(60 + (1.5 - peg) * 40)
        elif peg <= 2.5:
            dims["PEG合理性"] = round(40 - (peg - 1.5) * 20)
        else:
            dims["PEG合理性"] = round(max(5, 20 - (peg - 2.5) * 5))
    else:
        dims["PEG合理性"] = 45

    # Earnings growth
    npg = data.get("net_profit_growth")
    if npg is None:
        npg = data.get("revenue_growth")
    if npg is not None:
        if npg > 30:
            dims["盈利增长"] = round(_clamp(85 + min(npg - 30, 15), 0, 100))
        elif npg > 15:
            dims["盈利增长"] = round(60 + (npg - 15) * 1.67)
        elif npg > 0:
            dims["盈利增长"] = round(30 + npg * 2)
        else:
            dims["盈利增长"] = round(max(5, 30 + npg))
    else:
        dims["盈利增长"] = 40

    # Business understandability (simple heuristic)
    industry = data.get("industry", "")
    simple_industries = [
        "consumer", "retail", "food", "beverage", "bank", "insurance",
        "restaurant", "apparel", "healthcare", "pharmaceutical",
        "消费", "零售", "食品", "饮料", "银行", "保险", "医药", "餐饮",
        "家电", "服装", "日用",
    ]
    if any(kw in industry.lower() for kw in simple_industries):
        dims["业务可理解性"] = 85
    elif _is_innovation_industry(industry):
        dims["业务可理解性"] = 50
    else:
        dims["业务可理解性"] = 65

    # Financial health (combo of debt + ROE)
    debt_score = _score_inverse(data.get("debt_ratio"), 0, 80)
    roe_score = _score_linear(data.get("roe"), 0, 30)
    dims["财务健康"] = round((debt_score * 0.5 + roe_score * 0.5))

    # Growth space (smaller market cap = more room)
    mc = data.get("market_cap")
    if mc is not None:
        if mc < 5e9:
            mc_score = 95
        elif mc < 20e9:
            mc_score = 80
        elif mc < 100e9:
            mc_score = 60
        elif mc < 500e9:
            mc_score = 40
        else:
            mc_score = 25
    else:
        mc_score = 50
    growth_bonus = min(20, max(0, (data.get("revenue_growth") or 0) * 0.5))
    dims["成长空间"] = round(_clamp(mc_score + growth_bonus, 0, 100))

    # Valuation
    pe = data.get("pe")
    if pe is not None and pe > 0:
        if pe <= 15:
            dims["估值水平"] = 90
        elif pe <= 25:
            dims["估值水平"] = round(90 - (pe - 15) * 3)
        elif pe <= 40:
            dims["估值水平"] = round(60 - (pe - 25) * 2)
        else:
            dims["估值水平"] = round(max(5, 30 - (pe - 40) * 0.5))
    else:
        dims["估值水平"] = 50

    weights = {
        "PEG合理性": 0.25, "盈利增长": 0.20, "业务可理解性": 0.15,
        "财务健康": 0.15, "成长空间": 0.15, "估值水平": 0.10,
    }
    total = sum(dims[k] * weights[k] for k in weights)
    total = round(_clamp(total, 0, 100))

    summary = _lynch_summary(data, dims, total)
    return {"score": total, "dimensions": dims, "summary": summary}


def _lynch_summary(data: Dict, dims: Dict, score: int) -> str:
    name = data.get("stock_name", data.get("stock_code", ""))
    parts = []
    if dims["PEG合理性"] >= 70:
        parts.append(f"PEG合理({data.get('peg', 'N/A')})")
    if dims["盈利增长"] >= 70:
        parts.append("盈利增长强劲")
    if dims["业务可理解性"] >= 70:
        parts.append("业务简单易懂")
    if dims["财务健康"] >= 70:
        parts.append("财务状况健康")

    risks = []
    if dims["PEG合理性"] < 40:
        risks.append("PEG偏高，估值不够合理")
    if dims["成长空间"] < 40:
        risks.append("市值较大，成长空间有限")
    if dims["盈利增长"] < 40:
        risks.append("盈利增长动力不足")

    if score >= 80:
        prefix = f"{name}高度符合彼得林奇成长合理估值框架。"
    elif score >= 60:
        prefix = f"{name}较好符合彼得林奇GARP投资理念。"
    elif score >= 40:
        prefix = f"{name}部分符合彼得林奇成长价值标准。"
    else:
        prefix = f"{name}不太符合彼得林奇投资框架。"

    strengths = "、".join(parts) if parts else "暂无突出亮点"
    risk_str = "、".join(risks) if risks else "风险可控"
    return f"{prefix}优势：{strengths}。风险提示：{risk_str}。"


# ===================================================================
# Strategy signals
# ===================================================================
def generate_strategy_signals(data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Generate signals for each strategy based on available data."""
    signals = {}

    # 1. Fundamental multi-factor
    roe = data.get("roe")
    pe = data.get("pe")
    rg = data.get("revenue_growth")
    fund_score = 0
    fund_reasons = []
    if roe and roe > 15:
        fund_score += 1
        fund_reasons.append(f"ROE {roe}%表现良好")
    if pe and 0 < pe < 30:
        fund_score += 1
        fund_reasons.append(f"PE {pe}估值合理")
    if rg and rg > 10:
        fund_score += 1
        fund_reasons.append(f"营收增长{rg}%")

    if fund_score >= 2:
        signals["fundamental"] = {"signal": "bullish", "reason": "、".join(fund_reasons)}
    elif fund_score == 1:
        signals["fundamental"] = {"signal": "neutral", "reason": "基本面指标表现中性，" + "、".join(fund_reasons)}
    else:
        signals["fundamental"] = {"signal": "bearish", "reason": "基本面指标偏弱，缺乏明显亮点"}

    # 2. Momentum
    pct = data.get("price_change_pct")
    if pct is not None:
        if pct > 2:
            signals["momentum"] = {"signal": "bullish", "reason": f"近期涨幅{pct}%，动量信号积极"}
        elif pct > -2:
            signals["momentum"] = {"signal": "neutral", "reason": f"近期涨跌幅{pct}%，趋势不明朗"}
        else:
            signals["momentum"] = {"signal": "bearish", "reason": f"近期跌幅{pct}%，动量信号偏弱"}
    else:
        signals["momentum"] = {"signal": "neutral", "reason": "价格数据不足，无法判断动量方向"}

    # 3. Sentiment (proxy: use price change + growth as sentiment indicator)
    sent_score = 0
    sent_reasons = []
    if pct and pct > 0:
        sent_score += 1
        sent_reasons.append("近期价格走势积极")
    if rg and rg > 15:
        sent_score += 1
        sent_reasons.append("营收高增长提振市场信心")
    if data.get("market_cap") and data["market_cap"] > 100e9:
        sent_score += 1
        sent_reasons.append("大市值标的关注度高")

    if sent_score >= 2:
        signals["sentiment"] = {"signal": "bullish", "reason": "、".join(sent_reasons)}
    elif sent_score == 1:
        signals["sentiment"] = {"signal": "neutral", "reason": "市场情绪中性，" + "、".join(sent_reasons)}
    else:
        signals["sentiment"] = {"signal": "bearish", "reason": "市场情绪偏谨慎"}

    return signals


# ===================================================================
# Comprehensive conclusion
# ===================================================================
def generate_conclusion(
    data: Dict[str, Any],
    buffett: Dict, ark: Dict, lynch: Dict,
    strategies: Dict,
) -> Dict[str, Any]:
    """Generate overall conclusion."""
    # Best style
    scores = {"buffett": buffett["score"], "ark": ark["score"], "lynch": lynch["score"]}
    best = max(scores, key=scores.get)
    style_names = {"buffett": "巴菲特-芒格（质量价值）", "ark": "木头姐ARK（颠覆创新）", "lynch": "彼得林奇（成长合理估值）"}

    # Advantages
    advantages = []
    if data.get("roe") and data["roe"] > 20:
        advantages.append(f"ROE达{data['roe']}%，盈利能力突出")
    if data.get("revenue_growth") and data["revenue_growth"] > 20:
        advantages.append(f"营收增长{data['revenue_growth']}%，成长动力强劲")
    if data.get("gross_margin") and data["gross_margin"] > 50:
        advantages.append(f"毛利率{data['gross_margin']}%，护城河深厚")
    if data.get("peg") and 0 < data["peg"] < 1.5:
        advantages.append(f"PEG仅{data['peg']}，成长性价比高")
    if data.get("free_cash_flow") and data["free_cash_flow"] > 0:
        advantages.append("自由现金流为正，财务质量好")
    if data.get("debt_ratio") and data["debt_ratio"] < 30:
        advantages.append(f"负债率仅{data['debt_ratio']}%，财务稳健")
    # Ensure at least 1 advantage
    if not advantages:
        advantages.append("具备一定的投资价值")

    # Risks
    risks = []
    if data.get("pe") and data["pe"] > 50:
        risks.append(f"PE达{data['pe']}，估值偏高")
    if data.get("debt_ratio") and data["debt_ratio"] > 60:
        risks.append(f"负债率{data['debt_ratio']}%，财务杠杆偏高")
    if data.get("revenue_growth") and data["revenue_growth"] < 0:
        risks.append(f"营收下滑{data['revenue_growth']}%，增长承压")
    if data.get("roe") and data["roe"] < 10:
        risks.append(f"ROE仅{data['roe']}%，盈利能力偏弱")
    if not risks:
        risks.append("暂无明显风险信号")

    # Overall score (weighted average of three styles)
    overall = round(buffett["score"] * 0.35 + ark["score"] * 0.30 + lynch["score"] * 0.35)

    return {
        "overall_score": overall,
        "best_style": best,
        "best_style_name": style_names[best],
        "advantages": advantages[:3],
        "risks": risks[:3],
    }
