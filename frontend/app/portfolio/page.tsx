"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import {
  TrendingUp, TrendingDown, Wallet, PieChart, DollarSign, AlertCircle, Loader2,
} from "lucide-react";
import { clsx } from "clsx";
import type { Portfolio } from "@/lib/types";
import { tradingApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function PortfolioPage() {
  const { user, getToken } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) router.push("/login");
  }, [user, router]);

  const token = getToken();

  const { data, isLoading, error } = useSWR<Portfolio>(
    token ? "portfolio" : null,
    () => tradingApi.portfolio(token!),
    { refreshInterval: 30_000 }
  );

  if (!user) return null;

  const summary = data?.summary;
  const holdings = data?.holdings ?? [];
  const isPnlPositive = (summary?.total_pnl ?? 0) >= 0;

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-white">Portfolio</h1>
        <p className="mt-1 text-sm text-gray-500">Your current holdings and P&amp;L — refreshes every 30s</p>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Wallet className="h-5 w-5 text-cyan-400" />
                <div>
                  <p className="text-xs text-gray-500">Cash Balance</p>
                  <p className="text-lg font-bold text-white">
                    ₹{summary.balance.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <DollarSign className="h-5 w-5 text-blue-400" />
                <div>
                  <p className="text-xs text-gray-500">Invested</p>
                  <p className="text-lg font-bold text-white">
                    ₹{summary.total_invested.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <PieChart className="h-5 w-5 text-purple-400" />
                <div>
                  <p className="text-xs text-gray-500">Current Value</p>
                  <p className="text-lg font-bold text-white">
                    ₹{summary.total_current_value.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                {isPnlPositive ? (
                  <TrendingUp className="h-5 w-5 text-green-400" />
                ) : (
                  <TrendingDown className="h-5 w-5 text-red-400" />
                )}
                <div>
                  <p className="text-xs text-gray-500">Total P&amp;L</p>
                  <p className={clsx("text-lg font-bold", isPnlPositive ? "text-green-400" : "text-red-400")}>
                    {isPnlPositive ? "+" : ""}₹{summary.total_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    <span className="ml-1 text-sm">
                      ({isPnlPositive ? "+" : ""}{summary.total_pnl_pct.toFixed(2)}%)
                    </span>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12 text-gray-500">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          Loading portfolio…
        </div>
      )}

      {/* Error */}
      {error && !isLoading && (
        <div className="flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4" />
          Failed to load portfolio data.
        </div>
      )}

      {/* Holdings table */}
      {!isLoading && holdings.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-gray-800">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-800 bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-400">Symbol</th>
                <th className="px-4 py-3 text-right font-medium text-gray-400">Qty</th>
                <th className="px-4 py-3 text-right font-medium text-gray-400">Avg Price</th>
                <th className="px-4 py-3 text-right font-medium text-gray-400">Current</th>
                <th className="px-4 py-3 text-right font-medium text-gray-400">Value</th>
                <th className="px-4 py-3 text-right font-medium text-gray-400">P&amp;L</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800 bg-gray-950">
              {holdings.map((h) => {
                const pos = h.profit_loss >= 0;
                return (
                  <tr key={h.symbol} className="transition-colors hover:bg-gray-900/50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-white">{h.symbol.replace(".NS", "")}</div>
                      <div className="text-xs text-gray-500">{h.symbol}</div>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-white">{h.quantity}</td>
                    <td className="px-4 py-3 text-right font-mono text-gray-400">
                      ₹{Number(h.average_price).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-white">
                      ₹{h.current_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-white">
                      ₹{h.current_value.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className={clsx("font-mono text-sm font-semibold", pos ? "text-green-400" : "text-red-400")}>
                        {pos ? "+" : ""}₹{h.profit_loss.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </div>
                      <Badge variant={pos ? "success" : "destructive"} className="text-xs mt-0.5">
                        {pos ? "+" : ""}{h.profit_loss_pct.toFixed(2)}%
                      </Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {!isLoading && holdings.length === 0 && !error && (
        <div className="py-16 text-center text-gray-500">
          <PieChart className="mx-auto mb-3 h-10 w-10 opacity-30" />
          <p className="font-medium">No holdings yet</p>
          <p className="mt-1 text-sm">Go to Markets and buy your first share.</p>
        </div>
      )}
    </div>
  );
}
