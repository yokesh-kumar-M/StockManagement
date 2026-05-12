export interface Stock {
  symbol: string;
  name: string;
  price_inr: number;
  change_percent: number;
  day_high?: number;
  day_low?: number;
  volume?: number;
  sector?: string;
}

export interface UserProfile {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  balance: number;
  created_at: string;
}

export interface Holding {
  id: number;
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  current_value: number;
  profit_loss: number;
  profit_loss_pct: number;
  updated_at: string;
}

export interface PortfolioSummary {
  total_invested: number;
  total_current_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  balance: number;
}

export interface Portfolio {
  holdings: Holding[];
  summary: PortfolioSummary;
}

export interface Transaction {
  id: number;
  symbol: string;
  stock_name: string;
  action: "BUY" | "SELL";
  quantity: number;
  price: number;
  total_value: number;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface OHLCVPoint {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface ChartStats {
  latest: number;
  open: number;
  min: number;
  max: number;
  avg: number;
  change: number;
  change_pct: number;
}

export interface ChartData {
  symbol: string;
  period: string;
  interval: string;
  ohlcv: OHLCVPoint[];
  stats: ChartStats;
}

export interface AuthTokens {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
}

export interface TradeRequest {
  symbol: string;
  quantity: number;
  action: "BUY" | "SELL";
}

export interface TradeResponse {
  message: string;
  symbol: string;
  quantity: number;
  price: number;
  total_value: number;
  new_balance: number;
}

export interface ApiError {
  error: string;
  status_code?: number;
}
