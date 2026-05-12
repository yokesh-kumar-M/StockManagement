"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { History, Trash2, ChevronLeft, ChevronRight, Loader2, AlertCircle } from "lucide-react";
import { clsx } from "clsx";
import type { PaginatedResponse, Transaction } from "@/lib/types";
import { transactionsApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

function fetcher(token: string, page: number) {
  return transactionsApi.list(token, { page });
}

export default function TransactionsPage() {
  const { user, getToken } = useAuth();
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    if (!user) router.push("/login");
  }, [user, router]);

  const token = getToken();

  const { data, isLoading, error, mutate } = useSWR<PaginatedResponse<Transaction>>(
    token ? `transactions-${page}` : null,
    () => fetcher(token!, page),
    { keepPreviousData: true }
  );

  async function handleClear() {
    if (!token || !confirm("Clear all transaction history?")) return;
    setClearing(true);
    try {
      await transactionsApi.clear(token);
      mutate();
    } finally {
      setClearing(false);
    }
  }

  if (!user) return null;

  const transactions = data?.results ?? [];
  const totalPages = data ? Math.ceil(data.count / 20) : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Transaction History</h1>
          {data && (
            <p className="mt-1 text-sm text-gray-500">
              {data.count} transaction{data.count !== 1 ? "s" : ""} total
            </p>
          )}
        </div>
        {transactions.length > 0 && (
          <Button
            variant="destructive"
            size="sm"
            isLoading={clearing}
            onClick={handleClear}
            className="gap-2"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear All
          </Button>
        )}
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12 text-gray-500">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          Loading transactions…
        </div>
      )}

      {error && !isLoading && (
        <div className="flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4" />
          Failed to load transactions.
        </div>
      )}

      {!isLoading && transactions.length > 0 && (
        <>
          <div className="overflow-hidden rounded-xl border border-gray-800">
            <table className="w-full text-sm">
              <thead className="border-b border-gray-800 bg-gray-900">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-400">Stock</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-400">Action</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-400">Qty</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-400">Price</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-400">Total</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-400">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 bg-gray-950">
                {transactions.map((t) => (
                  <tr key={t.id} className="transition-colors hover:bg-gray-900/50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-white">{t.stock_name}</div>
                      <div className="text-xs text-gray-500">{t.symbol}</div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <Badge variant={t.action === "BUY" ? "success" : "destructive"}>
                        {t.action}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-white">{t.quantity}</td>
                    <td className="px-4 py-3 text-right font-mono text-gray-300">
                      ₹{Number(t.price).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-right font-mono font-semibold text-white">
                      ₹{Number(t.total_value).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-gray-500">
                      {new Date(t.timestamp).toLocaleString("en-IN", {
                        day: "2-digit",
                        month: "short",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {!isLoading && transactions.length === 0 && !error && (
        <div className="py-16 text-center text-gray-500">
          <History className="mx-auto mb-3 h-10 w-10 opacity-30" />
          <p className="font-medium">No transactions yet</p>
          <p className="mt-1 text-sm">Your trade history will appear here.</p>
        </div>
      )}
    </div>
  );
}
