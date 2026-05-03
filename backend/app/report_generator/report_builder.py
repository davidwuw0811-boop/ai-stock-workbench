from app.models.schemas import ScreeningResult


def build_markdown_report(result: ScreeningResult, disclaimer: str) -> str:
    thesis = "\n".join([f"- {item}" for item in result.thesis])
    risks = "\n".join([f"- {item}" for item in result.risks])
    scores = "\n".join([f"- {name}: {score:.1f}/100" for name, score in result.strategy_scores.items()])

    return f"""# {result.name} ({result.ticker}) AI 投研卡片

## 综合结论

- 市场：{result.market.value}
- 行业：{result.sector}
- 当前价格：{result.price} {result.currency}
- 综合评分：**{result.overall_score:.1f}/100**
- 适配判断：{result.suitability}

## 策略评分

{scores}

## 主要逻辑

{thesis}

## 风险提示

{risks}

---

**免责声明**：{disclaimer}
"""
