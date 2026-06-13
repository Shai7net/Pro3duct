"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { devLogin, getMe, logout as apiLogout, UserResponse, getAuthToken } from "@/lib/api";

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  loginUser: (token: string) => Promise<void>;
  logoutUser: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const refreshUser = async () => {
    try {
      if (!getAuthToken()) {
        await devLogin();
      }
      const data = await getMe();
      setUser(data);
    } catch (err) {
      console.error("Failed to load user:", err);
      apiLogout();
      try {
        await devLogin();
        setUser(await getMe());
      } catch {
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  // Handle protected pages navigation
  useEffect(() => {
    if (loading) return;

    const publicPages = ["/", "/login", "/register"];
    const isPublicPage = publicPages.includes(pathname) || pathname.startsWith("/embed/");

    if (!user && !isPublicPage) {
      router.push("/login");
    } else if (user && publicPages.includes(pathname)) {
      router.push("/dashboard");
    }
  }, [user, loading, pathname, router]);

  const loginUser = async (token: string) => {
    setLoading(true);
    await refreshUser();
    router.push("/dashboard");
  };

  const logoutUser = () => {
    apiLogout();
    setUser(null);
    setLoading(true);
    void refreshUser();
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginUser, logoutUser, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
