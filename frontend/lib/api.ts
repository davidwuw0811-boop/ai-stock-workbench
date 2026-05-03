export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export type Market = 'US' | 'CN';
export type RiskProfile = 'conservative' | 'balanced' | 'aggressive';
export type StrategyName = 'fundamental' | 'momentum' | 'sentiment' | 'finrl' | 'llm_agent';

export interface ScreeningResult {
  ticker: string;
  name: string;
  market: Market;
  sector: string;
  price: number;
  currency: string;
  overall_score: number;
  strategy_scores: Record<string, number>;
  thesis: string[];
  risks: string[];
  suitability: string;
}

export interface ScreeningResponse {
  market: Market;
  risk_profile: RiskProfile;
  results: ScreeningResult[];
  disclaimer: string;
}

export async function runScreening(payload: {
  market: Market;
  strategies: StrategyName[];
  risk_profile: RiskProfile;
  top_n: number;
}): Promise<ScreeningResponse> {
  const response = await fetch(`${API_BASE_URL}/api/screening`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Screening failed: ${response.status}`);
  }

  return response.json();
}
