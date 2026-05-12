"use client";

import { useCallback, useEffect, useState } from "react";
import useSWR from "swr";
import { RefreshCw, TrendingUp, Wallet, AlertCircle } from "lucide-react";
import type { Stock } from "@/lib/types";
import { stocksApi, profileApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { StockTable } from "@/components/StockTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

async function fetchStocks() {
  const res = await stocksApi.list();
  return res.stocks;
}

export default function HomePage() {
  const { user, getToken } = useAuth();
  const [holdings, setHoldings] = useState<Record<string, number>>({});
  const [balance, setBalance] = useState<number | null>(null);

  const {
    data: stocks,
    isLoading,
    mutate,
    error,
  } = useSWR<Stock[]>("stocks", fetchStocks, {
    refreshInterval: 30_000, // refresh every 30s
    revalidateOnFocus: false,
    dedupingInterval: 15_000,
  });

  const loadProfile = useCallback(async () => {
    const token = getToken();
    if (!token || !user) return;
    try {
      const [profile, portfolioRes] = await Promise.all([
        profileApi.get(token),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/portfolio/`, {
          headers: { Authorization: `Bearer ${token}` },
        }).then((r) => r.json()),
      ]);
      setBalance(Number(profile.balance));
      const h: Record<string, number> = {};
      for (const holding of portfolioRes.holdings ?? []) {
        h[holding.symbol] = holding.quantity;
      }
      setHoldings(h);
    } catch {}
  }, [user, getToken]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleTradeComplete = useCallback(() => {
    mutate();
    loadProfile();
  }, [mutate, loadProfile]);

  const visibleStocks = stocks ?? [];
  const totalStockValue = Object.entries(holdings).reduce((sum, [sym, qty]) => {
    const price = visibleStocks.find((s) => s.symbol === sym)?.price_inr ?? 0;
    return sum + price * qty;
  }, 0);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            Live Markets
            <span className="ml-3 rounded-full bg-green-500/10 px-2.5 py-1 text-sm font-medium text-green-400">
              NSE
            </span>
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time Indian equity prices · Refreshes every 30s
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => mutate()} className="gap-2">
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Stats cards (authenticated users only) */}
      {user && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Card>
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/10">
                <Wallet className="h-5 w-5 text-cyan-400" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Available Balance</p>
                <p className="text-lg font-bold text-white">
                  ₹{balance?.toLocaleString("en-IN", { minimumFractionDigits: 2 }) ?? "—"}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10">
                <TrendingUp className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Holdings Value</p>
                <p className="text-lg font-bold text-white">
                  ₹{totalStockValue.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-4 pt-6">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10">
                <TrendingUp className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Portfolio</p>
                <p className="text-lg font-bold text-white">
                  ₹{((balance ?? 0) + totalStockValue).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error state */}
      {error && !isLoading && (
        <div className="flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          Failed to load stock prices. The market data API may be rate-limited. Please wait a moment and refresh.
        </div>
      )}

      {/* Stock table */}
      <StockTable
        stocks={visibleStocks}
        holdings={holdings}
        onTradeComplete={handleTradeComplete}
      />

      {/* Login prompt */}
      {!user && (
        <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-6 text-center">
          <p className="text-gray-400">
            <a href="/login" className="font-semibold text-cyan-400 hover:underline">Login</a> or{" "}
            <a href="/register" className="font-semibold text-cyan-400 hover:underline">register</a>{" "}
            to start trading with ₹10,000 virtual money.
          </p>
        </div>
      )}
    </div>
  );
}
