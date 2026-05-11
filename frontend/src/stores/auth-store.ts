import { create } from "zustand";
import type { UserResponse } from "@/lib/types";

type AuthStore = {
  user: UserResponse | null;
  token: string | null;
  isLoading: boolean;
  isInitialized: boolean;
  setAuth: (user: UserResponse, token: string) => void;
  clearAuth: () => void;
  setLoading: (v: boolean) => void;
  setInitialized: (v: boolean) => void;
  hydrate: () => void;
};

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isLoading: true,
  isInitialized: false,
  setAuth: (user, token) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
      localStorage.setItem("auth_user", JSON.stringify(user));
      document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Lax`;
    }
    set({ user, token, isLoading: false, isInitialized: true });
  },
  clearAuth: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_user");
      document.cookie = "auth_token=; path=/; max-age=0";
    }
    set({ user: null, token: null, isLoading: false, isInitialized: true });
  },
  setLoading: (v) => set({ isLoading: v }),
  setInitialized: (v) => set({ isInitialized: v }),
  hydrate: () => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      const raw = localStorage.getItem("auth_user");
      if (token && raw) {
        try {
          const user = JSON.parse(raw) as UserResponse;
          set({ user, token, isLoading: false, isInitialized: true });
          return;
        } catch { /* corrupted data, clear */ }
      }
    }
    set({ isLoading: false, isInitialized: true });
  },
}));
