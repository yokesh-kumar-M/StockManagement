import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { AuthProvider } from "@/lib/auth";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: {
    default: "StockManager India — Live NSE/BSE Trading Simulator",
    template: "%s | StockManager India",
  },
  description:
    "Enterprise-grade Indian stock market portfolio manager. Trade NSE/BSE stocks in real-time, track your portfolio P&L, and analyze charts.",
  keywords: ["NSE", "BSE", "stock market", "portfolio", "India", "trading simulator"],
  openGraph: {
    title: "StockManager India",
    description: "Enterprise-grade Indian stock market portfolio manager",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#000000",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen bg-gray-950">
            <Navbar />
            <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
            <footer className="mt-16 border-t border-gray-800 py-8 text-center text-sm text-gray-600">
              StockManager India &copy; {new Date().getFullYear()} — For educational purposes only. Not financial advice.
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
