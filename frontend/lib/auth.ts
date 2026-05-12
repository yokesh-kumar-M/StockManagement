"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import type { AuthTokens } from "./types";

interface AuthState {
  user: AuthTokens["user"] | null;
  accessToken: string | null;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, password2: string) => Promise<void>;
  logout: () => void;
  getToken: () => string | null;
}

const TOKEN_KEY = "sm_access";
const REFRESH_KEY = "sm_refresh";
const USER_KEY = "sm_user";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthTokens["user"] | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function storeTokens(tokens: AuthTokens) {
  localStorage.setItem(TOKEN_KEY, tokens.access);
  localStorage.setItem(REFRESH_KEY, tokens.refresh);
  localStorage.setItem(USER_KEY, JSON.stringify(tokens.user));
}

function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

import React from "react";

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    isLoading: true,
  });

  useEffect(() => {
    const token = getStoredToken();
    const user = getStoredUser();
    setState({ user, accessToken: token, isLoading: false });
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const API = process.env.NEXT_PUBLIC_API_URL ?? "";
    const resp = await fetch(`${API}/api/v1/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.error ?? err.detail ?? "Login failed");
    }
    const data: AuthTokens = await resp.json();
    storeTokens(data);
    setState({ user: data.user, accessToken: data.access, isLoading: false });
  }, []);

  const register = useCallback(async (
    username: string, email: string, password: string, password2: string
  ) => {
    const API = process.env.NEXT_PUBLIC_API_URL ?? "";
    const resp = await fetch(`${API}/api/v1/auth/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password, password2 }),
    });
    if (!resp.ok) {
      const err = await resp.json();
      const first = Object.values(err)[0];
      throw new Error(Array.isArray(first) ? first[0] : String(first));
    }
    const data: AuthTokens = await resp.json();
    storeTokens(data);
    setState({ user: data.user, accessToken: data.access, isLoading: false });
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setState({ user: null, accessToken: null, isLoading: false });
  }, []);

  const getToken = useCallback(() => getStoredToken(), []);

  return React.createElement(
    AuthContext.Provider,
    { value: { ...state, login, register, logout, getToken } },
    children
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
