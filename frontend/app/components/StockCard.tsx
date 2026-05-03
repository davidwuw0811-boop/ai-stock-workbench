import type { ScreeningResult } from '@/lib/api';

const strategyLabels: Record<string, string> = {
  fundamental: '基本面',
  momentum: '动量',
  sentiment: '情绪',
  finrl: '强化学习',
  llm_agent: 'LLM Agent'
};

export function StockCard({ stock }: { stock: ScreeningResult }) {
  return (
    <article className="stock-card">
      <div className="stock-card-header">
        <div>
          <div className="ticker">{stock.ticker}</div>
          <div className="name">{stock.name}</div>
          <div className="sector">{stock.sector} · {stock.price} {stock.currency}</div>
        </div>
        <div className="score">{stock.overall_score.toFixed(1)}<small>/100</small></div>
      </div>

      <div className="score-grid">
        {Object.entries(stock.strategy_scores).map(([name, score]) => (
          <span className="badge" key={name}>{strategyLabels[name] || name}: {score.toFixed(1)}</span>
        ))}
      </div>

      <div className="badge">{stock.suitability}</div>

      <div className="columns">
        <div>
          <strong>主要逻辑</strong>
          <ul>
            {stock.thesis.slice(0, 5).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
        <div>
          <strong>风险提示</strong>
          <ul>
            {stock.risks.slice(0, 5).map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </div>
    </article>
  );
}
