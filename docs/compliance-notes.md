# Compliance Notes｜合规说明

## 重要声明

本项目仅用于研究、教育、产品原型演示，不构成投资建议。

在任何公开产品、商业化服务或社群销售场景中，建议避免使用以下表达：

- AI 荐股
- 保证收益
- 稳赚不赔
- 自动买入卖出
- 牛股推荐
- 内幕信号
- 跟着买就行

建议使用以下表达：

- AI 投研辅助
- 候选股票池
- 策略评分
- 风险提示
- 研究报告
- 模拟组合
- 教育用途

## 风险点

### 1. 投资顾问资质

如果产品向用户提供个性化买卖建议，尤其是收费服务，可能涉及证券投资咨询、投顾或 robo-adviser 监管问题。

### 2. 数据授权

开源代码协议不等于数据可以商用。行情、财务、新闻、社媒数据都需要单独确认授权。

### 3. 回测误导

回测结果必须披露：

- 时间区间
- 样本范围
- 交易成本
- 滑点
- 幸存者偏差
- 最大回撤
- 是否使用未来函数

### 4. 自动交易

不建议 MVP 阶段接入真实券商交易。先做研究、模拟盘、组合跟踪。

## 推荐产品口径

> AI Stock Workbench helps users research stocks, compare strategy signals, understand risks, and generate research notes. It does not provide personalized financial advice.
