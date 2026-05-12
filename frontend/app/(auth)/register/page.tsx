"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { TrendingUp, CheckCircle2 } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: "", email: "", password: "", password2: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (form.password !== form.password2) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    setIsLoading(true);
    try {
      await register(form.username, form.email, form.password, form.password2);
      router.push("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setIsLoading(false);
    }
  }

  const perks = [
    "₹10,000 virtual trading balance",
    "Real-time NSE/BSE stock prices",
    "Live portfolio P&L tracking",
    "Full trade history",
  ];

  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
      <div className="grid w-full max-w-3xl gap-12 md:grid-cols-2">
        {/* Left pane */}
        <div className="hidden flex-col justify-center space-y-6 md:flex">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-8 w-8 text-cyan-400" />
            <span className="text-2xl font-bold text-white">StockManager</span>
          </div>
          <h2 className="text-3xl font-bold text-white leading-tight">
            Start trading<br />the Indian markets
          </h2>
          <ul className="space-y-3">
            {perks.map((p) => (
              <li key={p} className="flex items-center gap-3 text-gray-400 text-sm">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-cyan-400" />
                {p}
              </li>
            ))}
          </ul>
        </div>

        {/* Right pane */}
        <div className="space-y-5">
          <div className="text-center md:text-left">
            <h1 className="text-xl font-semibold text-white">Create account</h1>
            <p className="mt-1 text-sm text-gray-500">Free forever. No credit card required.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-gray-800 bg-gray-900 p-6">
            {error && (
              <div className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
                {error}
              </div>
            )}

            <Input
              id="username"
              label="Username"
              value={form.username}
              onChange={update("username")}
              required
              minLength={3}
              placeholder="Choose a username"
              autoComplete="username"
            />
            <Input
              id="email"
              label="Email"
              type="email"
              value={form.email}
              onChange={update("email")}
              required
              placeholder="you@example.com"
              autoComplete="email"
            />
            <Input
              id="password"
              label="Password"
              type="password"
              value={form.password}
              onChange={update("password")}
              required
              minLength={8}
              placeholder="Min. 8 characters"
              autoComplete="new-password"
            />
            <Input
              id="password2"
              label="Confirm Password"
              type="password"
              value={form.password2}
              onChange={update("password2")}
              required
              placeholder="Repeat your password"
              autoComplete="new-password"
            />

            <Button type="submit" isLoading={isLoading} className="w-full mt-2">
              Create Account
            </Button>
          </form>

          <p className="text-center text-sm text-gray-500">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-cyan-400 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
