'use client';

import { useState } from 'react';
import { runScreening, type Market, type RiskProfile, type ScreeningResponse, type StrategyName } from '@/lib/api';
import { StockCard } from './components/StockCard';

const strategies: Array<{ value: StrategyName; label: string; description: string }> = [
  { value: 'fundamental', label: '基本面多因子', description: '估值、ROE、成长性、资产负债表' },
  { value: 'momentum', label: '动量趋势', description: '价格强度、趋势、波动率' },
  { value: 'sentiment', label: '情绪分析', description: '新闻、社媒、市场叙事热度' },
  { value: 'finrl', label: '强化学习择时', description: '预留 FinRL / FinRL-Trading 接口' },
  { value: 'llm_agent', label: 'LLM 投研 Agent', description: '预留大模型投研总结接口' }
];

export default function HomePage() {
  const [market, setMarket] = useState<Market>('US');
  const [riskProfile, setRiskProfile] = useState<RiskProfile>('balanced');
  const [selectedStrategies, setSelectedStrategies] = useState<StrategyName[]>(['fundamental', 'momentum', 'sentiment', 'finrl', 'llm_agent']);
  const [data, setData] = useState<ScreeningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggleStrategy(strategy: StrategyName) {
    setSelectedStrategies((current) =>
      current.includes(strategy)
        ? current.filter((item) => item !== strategy)
        : [...current, strategy]
    );
  }

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    try {
      const response = await runScreening({
        market,
        strategies: selectedStrategies,
        risk_profile: riskProfile,
        top_n: 5
      });
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <section className="hero">
        <div className="eyebrow">AI Stock Research Workbench</div>
        <h1>普通人的 AI 投研工作台</h1>
        <p className="subtitle">
          多因子选股 + 情绪分析 + 强化学习择时接口 + LLM 投研解释。不是自动荐股神器，而是帮助用户理解机会、风险和策略差异的研究工具。
        </p>
      </section>

      <section className="grid">
        <aside className="panel">
          <div className="field">
            <label>选择市场</label>
            <select value={market} onChange={(event) => setMarket(event.target.value as Market)}>
              <option value="US">美股 US</option>
              <option value="CN">A股 CN</option>
            </select>
          </div>

          <div className="field">
            <label>风险偏好</label>
            <select value={riskProfile} onChange={(event) => setRiskProfile(event.target.value as RiskProfile)}>
              <option value="conservative">稳健</option>
              <option value="balanced">平衡</option>
              <option value="aggressive">激进</option>
            </select>
          </div>

          <div className="field">
            <label>策略模块</label>
            <div className="strategy-list">
              {strategies.map((strategy) => (
                <label className="strategy-item" key={strategy.value}>
                  <input
                    type="checkbox"
                    checked={selectedStrategies.includes(strategy.value)}
                    onChange={() => toggleStrategy(strategy.value)}
                  />
                  <span>
                    <strong>{strategy.label}</strong>
                    <br />
                    <small>{strategy.description}</small>
                  </span>
                </label>
              ))}
            </div>
          </div>

          <button className="primary" onClick={handleSubmit} disabled={loading || selectedStrategies.length === 0}>
            {loading ? 'AI 正在分析...' : '生成 AI 候选池'}
          </button>

          <div className="disclaimer">
            本项目仅用于研究和教育目的，不构成任何投资建议，不承诺收益，不代客理财。
          </div>
        </aside>

        <section className="panel results">
          {error && <div className="disclaimer">{error}</div>}
          {!data && !error && <div className="empty">选择市场和策略，生成第一批 AI 候选股票池。</div>}
          {data?.results.map((stock) => <StockCard stock={stock} key={stock.ticker} />)}
          {data && <div className="disclaimer">{data.disclaimer}</div>}
        </section>
      </section>
    </main>
  );
}
