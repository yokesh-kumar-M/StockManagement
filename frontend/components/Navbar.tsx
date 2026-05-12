"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { TrendingUp, BarChart2, History, LogOut, LogIn, UserPlus, Wallet } from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "@/lib/auth";
import { Button } from "./ui/button";

const navLinks = [
  { href: "/", label: "Markets", icon: TrendingUp },
  { href: "/portfolio", label: "Portfolio", icon: Wallet, auth: true },
  { href: "/transactions", label: "History", icon: History, auth: true },
  { href: "/chart", label: "Charts", icon: BarChart2 },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-950/95 backdrop-blur supports-[backdrop-filter]:bg-gray-950/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-cyan-400" />
          <span className="text-lg font-bold text-white">
            Stock<span className="text-cyan-400">Manager</span>
          </span>
          <span className="hidden rounded-full bg-cyan-500/10 px-2 py-0.5 text-xs font-medium text-cyan-400 sm:inline">
            India
          </span>
        </Link>

        {/* Nav links */}
        <div className="hidden items-center gap-1 md:flex">
          {navLinks
            .filter((l) => !l.auth || user)
            .map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={clsx(
                  "flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  pathname === href
                    ? "bg-cyan-500/10 text-cyan-400"
                    : "text-gray-400 hover:bg-gray-800 hover:text-white"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
        </div>

        {/* Auth actions */}
        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="hidden text-sm text-gray-400 sm:block">
                Hi, <span className="font-medium text-white">{user.username}</span>
              </span>
              <Button variant="outline" size="sm" onClick={logout} className="gap-1.5">
                <LogOut className="h-3.5 w-3.5" />
                Logout
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm" className="gap-1.5">
                  <LogIn className="h-3.5 w-3.5" />
                  Login
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="gap-1.5">
                  <UserPlus className="h-3.5 w-3.5" />
                  Register
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
