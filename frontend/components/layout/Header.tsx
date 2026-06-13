"use client";

import React, { useEffect, useState } from "react";
import { Sparkles, ShieldCheck, ShieldAlert } from "lucide-react";
import { healthCheck } from "@/lib/api";

export default function Header() {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    healthCheck().then(() => setHealthy(true)).catch(() => setHealthy(false));
  }, []);

  return (
    <header
      style={{
        height: "var(--header-height)",
        width: "calc(100% - var(--sidebar-width))",
        position: "fixed",
        top: 0,
        left: 0,
        background: "rgba(8, 8, 16, 0.5)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid var(--glass-border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 32px",
        zIndex: 90,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <Sparkles size={16} style={{ color: "var(--primary)" }} />
        <span style={{ fontSize: "0.9rem", fontWeight: 500, color: "var(--text-secondary)" }}>סביבת פיתוח מקומית</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        {healthy === true ? (
          <>
            <ShieldCheck size={16} style={{ color: "var(--secondary)" }} />
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>המערכת מחוברת ומוכנה</span>
          </>
        ) : healthy === false ? (
          <>
            <ShieldAlert size={16} style={{ color: "var(--danger)" }} />
            <span style={{ fontSize: "0.85rem", color: "var(--danger)" }}>השרת אינו מחובר</span>
          </>
        ) : (
          <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>בודק את מצב המערכת...</span>
        )}
      </div>
    </header>
  );
}
