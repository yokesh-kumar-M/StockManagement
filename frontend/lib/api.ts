import type {
  Portfolio,
  PaginatedResponse,
  Transaction,
  TradeRequest,
  TradeResponse,
  ChartData,
  UserProfile,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${BASE}${path}`, { ...options, headers });

  if (!resp.ok) {
    let error = `HTTP ${resp.status}`;
    try {
      const data = await resp.json();
      error = data.error ?? data.detail ?? error;
    } catch {}
    throw new Error(error);
  }

  if (resp.status === 204) return {} as T;
  return resp.json();
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  login: (username: string, password: string) =>
    request<{ access: string; refresh: string; user: { id: number; username: string; email: string } }>(
      "/api/v1/auth/login/",
      { method: "POST", body: JSON.stringify({ username, password }) }
    ),
  register: (data: { username: string; email: string; password: string; password2: string }) =>
    request("/api/v1/auth/register/", { method: "POST", body: JSON.stringify(data) }),
};

// ─── Stocks ───────────────────────────────────────────────────────────────────

export const stocksApi = {
  list: () => request<{ stocks: import("./types").Stock[]; count: number }>("/api/v1/stocks/"),
  chart: (symbol: string, period = "5d", interval = "1h") =>
    request<ChartData>(`/api/v1/stocks/chart/?symbol=${symbol}&period=${period}&interval=${interval}`),
};

// ─── Profile ──────────────────────────────────────────────────────────────────

export const profileApi = {
  get: (token: string) => request<UserProfile>("/api/v1/profile/", {}, token),
};

// ─── Trading ──────────────────────────────────────────────────────────────────

export const tradingApi = {
  trade: (data: TradeRequest, token: string) =>
    request<TradeResponse>("/api/v1/trade/", { method: "POST", body: JSON.stringify(data) }, token),
  portfolio: (token: string) => request<Portfolio>("/api/v1/portfolio/", {}, token),
  withdraw: (amount: number, token: string) =>
    request("/api/v1/withdraw/", { method: "POST", body: JSON.stringify({ amount }) }, token),
};

// ─── Transactions ─────────────────────────────────────────────────────────────

export const transactionsApi = {
  list: (token: string, params?: { action?: string; symbol?: string; page?: number }) => {
    const qs = new URLSearchParams();
    if (params?.action) qs.set("action", params.action);
    if (params?.symbol) qs.set("symbol", params.symbol);
    if (params?.page) qs.set("page", String(params.page));
    const query = qs.toString() ? `?${qs}` : "";
    return request<PaginatedResponse<Transaction>>(`/api/v1/transactions/${query}`, {}, token);
  },
  clear: (token: string) =>
    request("/api/v1/transactions/clear/", { method: "DELETE" }, token),
};

// ─── Health ───────────────────────────────────────────────────────────────────

export const healthApi = {
  check: () => request<{ status: string; version: string }>("/api/v1/health/"),
};
