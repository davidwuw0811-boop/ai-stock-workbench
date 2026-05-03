# AI Stock Workbench｜AI 选股工作台

> AI-powered stock research workbench for screening, strategy comparison, risk analysis, and research report generation.  
> 一个面向普通投资者和研究者的 AI 投研工作台：多因子选股、强化学习择时接口、情绪分析、风险评分与投研报告生成。

![status](https://img.shields.io/badge/status-MVP-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![frontend](https://img.shields.io/badge/frontend-Next.js-black)

## 项目定位

AI Stock Workbench 不是“自动荐股神器”，而是一个 **AI 投研辅助平台**。它帮助用户：

- 从 A 股 / 美股股票池中筛选候选标的
- 比较基本面、动量、情绪、强化学习等多种策略信号
- 生成可解释的 AI 投研卡片和风险提示
- 预留 FinRL、AKShare、TuShare、Yahoo Finance、LLM Agent 等扩展接口

> 本项目仅用于研究、教育和产品原型演示，不构成任何证券、基金、期货、加密资产或其他金融产品的投资建议。

---

## MVP 功能

### 1. 多市场选择

- 美股 US Equities
- A股 China A-shares
- 后续可扩展：港股、ETF、加密资产

### 2. 多策略插件

当前内置策略：

- `fundamental`：基本面评分，包括估值、盈利质量、成长性、资产负债表
- `momentum`：动量评分，包括趋势、波动、近端价格强度
- `sentiment`：情绪评分，包括新闻、社媒、市场叙事热度的模拟接口
- `finrl`：强化学习择时策略适配器，占位接口，后续可接入 FinRL / FinRL-Trading
- `llm_agent`：LLM 投研总结接口，占位实现，后续可接 OpenAI / Claude / 本地模型

### 3. 输出结果

每只股票输出：

- 综合评分
- 策略分项评分
- 上涨逻辑
- 风险提示
- 适合投资者类型
- 研究用途免责声明

### 4. 回测接口

MVP 提供模拟回测结果结构，后续可接 Backtrader、VectorBT、FinRL、Zipline 等框架。

---

## 技术架构

```text
ai-stock-workbench/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   ├── core/               # 配置与免责声明
│   │   ├── data_providers/     # 数据源适配器
│   │   ├── models/             # Pydantic 数据模型
│   │   ├── strategies/         # 策略插件
│   │   ├── risk_engine/        # 风险评分
│   │   ├── report_generator/   # 投研报告生成
│   │   └── services/           # 业务编排
│   └── tests/
├── frontend/                   # Next.js 前端
├── docs/                       # 产品、架构、合规与插件文档
└── examples/                   # 示例请求与报告
```

---

## 快速开始

### 后端启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

访问：

```text
http://localhost:8000/docs
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

### Docker Compose

```bash
docker compose up --build
```

---

## API 示例

### POST `/api/screening`

```json
{
  "market": "US",
  "strategies": ["fundamental", "momentum", "sentiment", "finrl", "llm_agent"],
  "risk_profile": "balanced",
  "top_n": 5
}
```

### 示例返回

```json
{
  "market": "US",
  "risk_profile": "balanced",
  "results": [
    {
      "ticker": "MSFT",
      "name": "Microsoft",
      "overall_score": 86.5,
      "strategy_scores": {
        "fundamental": 88,
        "momentum": 82,
        "sentiment": 85,
        "finrl": 80,
        "llm_agent": 90
      },
      "thesis": ["云业务稳健", "AI 应用商业化持续推进"],
      "risks": ["估值偏高", "AI CapEx 可能压制利润率"],
      "suitability": "适合中长期成长型观察组合"
    }
  ],
  "disclaimer": "For research and educational purposes only. Not financial advice."
}
```

---

## 未来路线图

- [ ] 接入 AKShare / TuShare 获取 A 股数据
- [ ] 接入 yfinance / Polygon / Alpha Vantage 获取美股数据
- [ ] 接入 FinRL / FinRL-Trading 做强化学习训练与择时
- [ ] 接入真实新闻与社媒情绪分析
- [ ] 增加策略回测：年化收益、最大回撤、夏普比率、胜率、换手率
- [ ] 增加组合跟踪：持仓贡献、行业集中度、风险暴露
- [ ] 增加 LLM 自动投研报告生成
- [ ] 增加用户自定义策略插件系统

---

## 合规声明

本项目不提供任何个性化投资建议，不承诺收益，不代客理财，不自动执行交易。所有输出均为基于示例数据和模型规则生成的研究信息。用户应自行判断风险，并在必要时咨询持牌金融顾问。

---

## License

MIT License. See [LICENSE](LICENSE).
