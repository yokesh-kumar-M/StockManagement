"use client";

import { useState } from "react";
import useSWR from "swr";
import { BarChart2, Loader2, AlertCircle } from "lucide-react";
import type { ChartData } from "@/lib/types";
import { stocksApi } from "@/lib/api";
import { StockChart } from "@/components/StockChart";
import { Button } from "@/components/ui/button";

const SYMBOLS = [
  "TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS",
  "ITC.NS", "WIPRO.NS", "HCLTECH.NS", "SBIN.NS", "LT.NS",
];

const PERIODS = [
  { label: "1D", value: "1d", interval: "5m" },
  { label: "5D", value: "5d", interval: "1h" },
  { label: "1M", value: "1mo", interval: "1d" },
  { label: "3M", value: "3mo", interval: "1d" },
  { label: "1Y", value: "1y", interval: "1wk" },
];

export default function ChartPage() {
  const [symbol, setSymbol] = useState("TCS.NS");
  const [period, setPeriod] = useState(PERIODS[1]);

  const { data, isLoading, error } = useSWR<ChartData>(
    `chart-${symbol}-${period.value}`,
    () => stocksApi.chart(symbol, period.value, period.interval),
    { revalidateOnFocus: false, dedupingInterval: 60_000 }
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-white">Stock Charts</h1>
        <p className="mt-1 text-sm text-gray-500">Historical OHLC data for NSE equities</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-400">Stock</label>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="block rounded-md border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
          >
            {SYMBOLS.map((s) => (
              <option key={s} value={s}>{s.replace(".NS", "")}</option>
            ))}
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-400">Period</label>
          <div className="flex gap-1">
            {PERIODS.map((p) => (
              <Button
                key={p.value}
                variant={period.value === p.value ? "default" : "outline"}
                size="sm"
                onClick={() => setPeriod(p)}
                className="min-w-[3rem]"
              >
                {p.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart area */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="mb-4 flex items-center gap-2">
          <BarChart2 className="h-5 w-5 text-cyan-400" />
          <h2 className="text-lg font-semibold text-white">
            {symbol.replace(".NS", "")} — {period.label}
          </h2>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-24 text-gray-500">
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Fetching chart data…
          </div>
        )}

        {error && !isLoading && (
          <div className="flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            <AlertCircle className="h-4 w-4" />
            Failed to load chart data. Yahoo Finance may be rate-limiting. Try again in a moment.
          </div>
        )}

        {data && !isLoading && <StockChart data={data} />}
      </div>
    </div>
  );
}
