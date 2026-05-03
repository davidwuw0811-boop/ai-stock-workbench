# AI Stock Workbench — 投资大师风格引擎

> AI选股工作台：将巴菲特、ARK、彼得林奇等投资大师的公开理念转化为量化筛选因子，支持任意A股/美股实时分析

## 在线体验

- **GitHub Pages 版**：[https://davidwuw0811-boop.github.io/ai-stock-workbench/](https://davidwuw0811-boop.github.io/ai-stock-workbench/)
- **后端 API**：`https://ai-stock-workbench-production.up.railway.app`

## 功能特性

### 投资大师风格引擎
- **巴菲特-芒格（价值投资）**：高ROE、低负债、强现金流、护城河评估、估值合理性
- **木头姐ARK（颠覆创新）**：高增长、高研发、创新赛道、平台潜力、成长性溢价接受度
- **彼得林奇（成长价值）**：PEG合理、盈利增长、业务易懂、中小市值

### 五大策略模块
- 基本面多因子 📊
- 动量趋势 📈
- 情绪分析 💬
- FinRL强化学习 🤖
- LLM投研Agent 🧠

### 个股分析器
输入任意股票代码即可实时分析，无需加后缀：
- **美股**：直接输入代码，如 AAPL、TSLA、NVDA、CRM
- **A股**：直接输入6位代码，如 600519、300624、000001（系统自动识别上海/深圳）

分析输出：
- 各风格评分 + 雷达图
- 策略信号（看多/中性/看空）
- 综合结论（优势与风险）

### 数据可视化
- AI评分环形进度条
- 迷你K线图
- 价格走势图（带渐变填充）
- 成交量柱状图
- MA5/MA20均线叠加

## 项目结构

```
ai-stock-workbench/
├── index.html              # 纯前端版本（GitHub Pages）
├── backend/                # FastAPI 后端 API
│   ├── app/
│   │   ├── main.py         # FastAPI 路由 + CORS
│   │   ├── data_fetcher.py # 数据获取（yfinance，A股/美股统一）
│   │   └── scoring.py      # 三大投资风格评分模型
│   ├── requirements.txt    # Python 依赖
│   ├── Procfile            # Railway 部署配置
│   └── railway.json        # Railway 配置
└── README.md
```

## 后端 API

### 接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/search?q=xxx` | GET | 股票搜索/模糊匹配 |
| `/api/analyze/{stock_code}` | GET | 完整投资风格分析 |

### 数据源
- **A股 + 美股统一使用**：[yfinance](https://github.com/ranaroussi/yfinance)
  - A股自动转换：600xxx → .SS（上海），000xxx/300xxx → .SZ（深圳）
  - 覆盖：实时股价、PE、PB、ROE、毛利率、市值、现金流、研发费用等

### 评分模型

**巴菲特-芒格评分维度（权重）：**
- ROE质量(20%) + 负债水平(15%) + 盈利稳定性(15%) + 自由现金流(15%) + 护城河(15%) + 估值合理性(15%) + 管理层质量(5%)

**木头姐ARK评分维度（权重）：**
- 主题契合度(25%) + 收入增长(20%) + 研发强度(15%) + 平台潜力(15%) + 市场空间(15%) + 成长性溢价接受度(10%)
- 设计理念：Cathie Wood为了高成长愿意接受较高估值，高PE+高增长=高分，更贴近她"重成长、轻传统估值"的真实风格

**彼得林奇评分维度（权重）：**
- PEG合理性(25%) + 盈利增长(20%) + 业务可理解性(15%) + 财务健康(15%) + 成长空间(15%) + 估值水平(10%)

## 部署指南

### 方式一：GitHub Pages（纯前端 + Railway API）

1. Fork 本仓库
2. 在仓库 Settings → Pages 中启用 GitHub Pages
3. 选择 `main` 分支的根目录
4. 访问 `https://<username>.github.io/ai-stock-workbench/`
5. 前端自动连接 Railway 后端获取实时数据

### 方式二：Railway（后端 API）

1. 登录 [Railway](https://railway.app)
2. New Project → Deploy from GitHub Repo
3. 选择本仓库，设置 Root Directory 为 `backend`
4. Railway 会自动检测 Python 项目并部署
5. **重要**：在 Settings → Networking 中确认端口与应用监听端口一致
6. 部署成功后获取域名，如 `https://your-app.up.railway.app`

### 方式三：本地运行

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 测试
curl http://localhost:8000/api/health
curl http://localhost:8000/api/analyze/AAPL
curl http://localhost:8000/api/analyze/600519
curl http://localhost:8000/api/analyze/300624
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端（GitHub Pages版） | 纯 HTML/CSS/JS + Chart.js |
| 后端 | FastAPI + yfinance |
| 部署 | Railway（后端）+ GitHub Pages（前端） |

## 免责声明

本模型只是将公开投资理念转化为量化筛选因子，用于研究和教育，不代表巴菲特、芒格、Cathie Wood 或 ARK 的真实投资意见，也不构成投资建议。

## License

MIT
