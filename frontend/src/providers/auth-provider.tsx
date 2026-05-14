"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
} from "react";
import { useRouter } from "next/navigation";
import { loginUser, registerUser, getCurrentUser } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import type { UserResponse } from "@/lib/types";

type AuthContextType = {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInstructor: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const store = useAuthStore();

  useEffect(() => {
    store.hydrate();
    const token = localStorage.getItem("auth_token");
    if (token) {
      getCurrentUser()
        .then((user) => store.setAuth(user, token))
        .catch(() => store.clearAuth());
    } else {
      store.setInitialized(true);
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      store.setLoading(true);
      try {
        const result = await loginUser({ email, password });
        store.setAuth(result.user, result.access_token);
      } catch (error) {
        store.setLoading(false);
        throw error;
      }
    },
    [store]
  );

  const register = useCallback(
    async (email: string, password: string, displayName?: string) => {
      store.setLoading(true);
      try {
        const result = await registerUser({ email, password, display_name: displayName });
        store.setAuth(result.user, result.access_token);
      } catch (error) {
        store.setLoading(false);
        throw error;
      }
    },
    [store]
  );

  const logout = useCallback(() => {
    store.clearAuth();
    router.push("/login");
  }, [store, router]);

  const value = useMemo<AuthContextType>(
    () => ({
      user: store.user,
      token: store.token,
      isAuthenticated: Boolean(store.token && store.user),
      isLoading: store.isLoading,
      isInstructor: store.user?.role === "instructor",
      login,
      register,
      logout,
    }),
    [store.user, store.token, store.isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
