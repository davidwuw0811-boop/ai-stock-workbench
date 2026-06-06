"""
Piotroski F-Score 计算模块（已集成 data_fetcher）
"""

from typing import Dict, Any
from app.data_fetcher import get_piotroski_input_data   # 导入我们刚新增的函数


def calculate_piotroski_score(stock_code: str, use_akshare: bool = False) -> Dict[str, Any]:
    """
    计算 Piotroski F-Score（0-9分）
    推荐直接调用这个函数
    """
    # 使用 data_fetcher 统一获取数据
    data = get_piotroski_input_data(stock_code)
    
    if "error" in data:
        return {"score": 0, "error": data["error"], "breakdown": {}}
    
    breakdown = {}
    score = 0
    
    # ========== 盈利能力 (4分) ==========
    roa = data.get("net_income", 0) / data.get("total_assets", 1) if data.get("total_assets") else 0
    breakdown["roa_positive"] = 1 if roa > 0 else 0
    score += breakdown["roa_positive"]
    
    breakdown["cfo_positive"] = 1 if data.get("operating_cash_flow", 0) > 0 else 0
    score += breakdown["cfo_positive"]
    
    prev_roa = 0
    if data.get("previous_total_assets"):
        # 这里简化处理，实际可从 data 中扩展 previous_net_income
        prev_roa = data.get("net_income", 0) / data.get("previous_total_assets", 1)
    breakdown["roa_improving"] = 1 if roa > prev_roa else 0
    score += breakdown["roa_improving"]
    
    breakdown["cfo_gt_ni"] = 1 if data.get("operating_cash_flow", 0) > data.get("net_income", 0) else 0
    score += breakdown["cfo_gt_ni"]
    
    # ========== 财务杠杆与流动性 (2分) ==========
    debt_ratio = data.get("long_term_debt", 0) / data.get("total_assets", 1) if data.get("total_assets") else 0
    breakdown["debt_decreasing"] = 1 if debt_ratio < 0.3 else 0   # 简化判断
    score += breakdown["debt_decreasing"]
    
    current_ratio = data.get("current_assets", 0) / data.get("current_liabilities", 1) if data.get("current_liabilities") else 0
    breakdown["current_ratio_healthy"] = 1 if current_ratio > 1.0 else 0
    score += breakdown["current_ratio_healthy"]
    
    # ========== 运营效率 (2分) ==========
    gross_margin = data.get("gross_profit", 0) / data.get("total_revenue", 1) if data.get("total_revenue") else 0
    breakdown["gross_margin_positive"] = 1 if gross_margin > 0.2 else 0   # 简化
    score += breakdown["gross_margin_positive"]
    
    asset_turnover = data.get("total_revenue", 0) / data.get("total_assets", 1) if data.get("total_assets") else 0
    breakdown["asset_turnover_positive"] = 1 if asset_turnover > 0.5 else 0
    score += breakdown["asset_turnover_positive"]
    
    # 解读
    if score >= 7:
        interpretation = "财务健康状况优秀，改善信号明显"
    elif score >= 5:
        interpretation = "财务状况良好，具备一定安全边际"
    elif score >= 3:
        interpretation = "财务状况一般，需重点关注风险"
    else:
        interpretation = "财务健康度较低，建议谨慎"
    
    return {
        "stock_code": stock_code,
        "piotroski_score": score,
        "breakdown": breakdown,
        "details": {
            "roa": round(roa, 4),
            "gross_margin": round(gross_margin, 4),
            "current_ratio": round(current_ratio, 2),
            "asset_turnover": round(asset_turnover, 4),
        },
        "interpretation": interpretation,
        "max_score": 9
    }


if __name__ == "__main__":
    # 本地测试
    result = calculate_piotroski_score("600519")
    print(result)
