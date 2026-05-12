"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from "recharts";
import type { ChartData } from "@/lib/types";

interface Props {
  data: ChartData;
}

function fmt(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: { time: string; close: number } }> }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-md border border-gray-700 bg-gray-900 px-3 py-2 shadow-xl text-xs">
      <p className="text-gray-400">{new Date(d.time).toLocaleString("en-IN")}</p>
      <p className="font-semibold text-white">₹{d.close.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</p>
    </div>
  );
}

export function StockChart({ data }: Props) {
  const chartData = data.ohlcv.map((p) => ({ ...p, label: fmt(p.time) }));
  const isPositive = data.stats.change_pct >= 0;
  const color = isPositive ? "#4ade80" : "#f87171";
  const openPrice = data.stats.open;

  return (
    <div className="space-y-4">
      {/* Stats row */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Latest", value: data.stats.latest },
          { label: "Open", value: data.stats.open },
          { label: "High", value: data.stats.max },
          { label: "Low", value: data.stats.min },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-lg border border-gray-800 bg-gray-900 p-3">
            <p className="text-xs text-gray-500">{label}</p>
            <p className="mt-0.5 font-mono text-base font-semibold text-white">
              ₹{value.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </p>
          </div>
        ))}
      </div>

      {/* Change badge */}
      <div className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium ${
        isPositive ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
      }`}>
        {isPositive ? "▲" : "▼"} {isPositive ? "+" : ""}{data.stats.change.toFixed(2)} ({isPositive ? "+" : ""}{data.stats.change_pct.toFixed(2)}%)
      </div>

      {/* Chart */}
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis
              dataKey="label"
              tick={{ fill: "#6b7280", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#6b7280", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `₹${v.toLocaleString("en-IN")}`}
              width={80}
              domain={["auto", "auto"]}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={openPrice}
              stroke="#4b5563"
              strokeDasharray="4 4"
              label={{ value: "Open", fill: "#6b7280", fontSize: 11 }}
            />
            <Line
              type="monotone"
              dataKey="close"
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: color, stroke: "transparent" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
