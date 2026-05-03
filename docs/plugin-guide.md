# Plugin Guide｜策略插件开发指南

## 新增策略步骤

### 1. 创建策略文件

在 `backend/app/strategies/` 下新增文件，例如：

```text
quality_strategy.py
```

### 2. 继承 Strategy 基类

```python
from app.models.schemas import RiskProfile, StockCandidate, StrategyScore
from app.strategies.base import Strategy, clamp_score


class QualityStrategy(Strategy):
    name = "quality"

    def score(self, candidate: StockCandidate, risk_profile: RiskProfile) -> StrategyScore:
        roe = float(candidate.metrics.get("roe", 10))
        debt = float(candidate.metrics.get("debt_to_equity", 0.5))
        score = roe * 2 - debt * 10
        return StrategyScore(
            name=self.name,
            score=clamp_score(score),
            rationale=["基于 ROE 和杠杆水平评估质量"],
            risks=[]
        )
```

### 3. 注册策略

在 `backend/app/strategies/registry.py` 中加入：

```python
from app.strategies.quality_strategy import QualityStrategy

STRATEGY_REGISTRY = {
    ...,
    "quality": QualityStrategy(),
}
```

### 4. 更新前端

在 `frontend/app/page.tsx` 的 `strategies` 列表中增加新策略。

## 接入 FinRL 的建议

FinRL 不建议直接塞进主流程同步运行。更好的方式是：

1. 用离线任务训练 agent
2. 把模型和回测结果存入 artifacts
3. API 只读取最新策略信号和风险参数
4. 前端展示 timing confidence，而不是实时训练
