"use client";

import { useState } from "react";
import { TrendingUp, TrendingDown, BarChart2, Loader2 } from "lucide-react";
import Link from "next/link";
import { clsx } from "clsx";
import type { Stock } from "@/lib/types";
import { tradingApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

interface Props {
  stocks: Stock[];
  holdings: Record<string, number>;
  onTradeComplete: () => void;
}

export function StockTable({ stocks, holdings, onTradeComplete }: Props) {
  const { getToken, user } = useAuth();
  const [loadingKey, setLoadingKey] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function executeTrade(symbol: string, action: "BUY" | "SELL") {
    const token = getToken();
    if (!token) return;
    setLoadingKey(`${action}-${symbol}`);
    setError(null);
    try {
      await tradingApi.trade({ symbol, quantity: 1, action }, token);
      onTradeComplete();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Trade failed.");
    } finally {
      setLoadingKey(null);
    }
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-gray-800">
        <table className="w-full text-sm">
          <thead className="border-b border-gray-800 bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-400">Stock</th>
              <th className="px-4 py-3 text-right font-medium text-gray-400">Price (₹)</th>
              <th className="px-4 py-3 text-right font-medium text-gray-400">Change</th>
              <th className="px-4 py-3 text-center font-medium text-gray-400">Holdings</th>
              {user && <th className="px-4 py-3 text-center font-medium text-gray-400">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800 bg-gray-950">
            {stocks.map((stock) => {
              const held = holdings[stock.symbol] ?? 0;
              const isUp = stock.change_percent >= 0;
              return (
                <tr key={stock.symbol} className="transition-colors hover:bg-gray-900/50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-800 text-xs font-bold text-cyan-400">
                        {stock.symbol.replace(".NS", "").slice(0, 3)}
                      </div>
                      <div>
                        <div className="font-medium text-white">{stock.name}</div>
                        <div className="text-xs text-gray-500">{stock.symbol}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right font-mono font-semibold text-white">
                    ₹{stock.price_inr.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span
                      className={clsx(
                        "inline-flex items-center gap-0.5 text-sm font-medium",
                        isUp ? "text-green-400" : "text-red-400"
                      )}
                    >
                      {isUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      {isUp ? "+" : ""}
                      {stock.change_percent.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {held > 0 ? (
                      <Badge variant="success">{held} share{held > 1 ? "s" : ""}</Badge>
                    ) : (
                      <span className="text-xs text-gray-600">—</span>
                    )}
                  </td>
                  {user && (
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-center gap-2">
                        <Button
                          variant="success"
                          size="sm"
                          isLoading={loadingKey === `BUY-${stock.symbol}`}
                          onClick={() => executeTrade(stock.symbol, "BUY")}
                        >
                          Buy
                        </Button>
                        <Button
                          variant="warning"
                          size="sm"
                          isLoading={loadingKey === `SELL-${stock.symbol}`}
                          disabled={held === 0}
                          onClick={() => executeTrade(stock.symbol, "SELL")}
                        >
                          Sell
                        </Button>
                        <Link href={`/chart?symbol=${stock.symbol}`}>
                          <Button variant="outline" size="sm">
                            <BarChart2 className="h-3.5 w-3.5" />
                          </Button>
                        </Link>
                      </div>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>

        {stocks.length === 0 && (
          <div className="flex items-center justify-center py-16 text-gray-500">
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Loading live prices…
          </div>
        )}
      </div>
    </div>
  );
}
