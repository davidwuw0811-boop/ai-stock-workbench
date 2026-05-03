# Architecture｜技术架构

## 总体结构

```text
Frontend Next.js
      |
      v
Backend FastAPI
      |
      +-- Data Providers
      +-- Strategy Plugins
      +-- Risk Engine
      +-- Report Generator
      +-- Backtest Engine
```

## 后端模块

### Data Providers

统一数据接口，未来可接：

- AKShare
- TuShare
- yfinance
- Polygon
- Alpha Vantage
- Wind / Choice 商业数据

### Strategy Plugins

所有策略继承 `Strategy` 基类，实现：

```python
def score(candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
    ...
```

当前内置：

- FundamentalStrategy
- MomentumStrategy
- SentimentStrategy
- FinRLAdapterStrategy
- LLMAgentStrategy

### Risk Engine

负责把估值、波动率、杠杆、风险偏好转成用户可理解的风险提示。

### Report Generator

把结构化结果转为 Markdown 投研卡片，未来可接 LLM 生成更自然的报告。

## 前端模块

Next.js 单页应用：

- 市场选择
- 风险偏好选择
- 策略选择
- 候选股票卡片
- 策略分数和风险提示

## 生产化建议

1. 数据源必须可追溯
2. 回测必须显示交易成本、滑点、最大回撤
3. 所有“建议”都要改为“研究结果 / 候选池 / 风险提示”
4. 不要直接接实盘交易，先做模拟盘
