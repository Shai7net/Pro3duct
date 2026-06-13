"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FolderKanban, Settings, LogOut } from "lucide-react";
import { useAuth } from "@/components/providers/AuthProvider";

export default function Sidebar() {
  const pathname = usePathname();
  const { logoutUser, user } = useAuth();

  const navItems = [
    { name: "מסך ראשי", href: "/dashboard", icon: LayoutDashboard },
    { name: "הפרויקטים שלי", href: "/dashboard/projects", icon: FolderKanban },
    { name: "הגדרות", href: "/dashboard/settings", icon: Settings },
  ];

  return (
    <aside
      style={{
        width: "var(--sidebar-width)",
        height: "100vh",
        position: "fixed",
        top: 0,
        right: 0,
        background: "rgba(10, 11, 26, 0.85)",
        backdropFilter: "blur(20px)",
        borderLeft: "1px solid var(--glass-border)",
        display: "flex",
        flexDirection: "column",
        zIndex: 100,
      }}
    >
      <div
        style={{
          height: "var(--header-height)",
          display: "flex",
          alignItems: "center",
          padding: "0 24px",
          borderBottom: "1px solid var(--glass-border)",
        }}
      >
        <Link
          href="/dashboard"
          style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none", color: "var(--text-primary)" }}
        >
          <span style={{ fontSize: "1.2rem", color: "var(--primary)", fontWeight: 900 }}>P3</span>
          <span style={{ fontWeight: 800, fontSize: "1.2rem" }}>Pro3duct</span>
        </Link>
      </div>

      <nav style={{ flex: 1, padding: "24px 16px", display: "flex", flexDirection: "column", gap: "8px" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "12px 16px",
                borderRadius: "var(--border-radius)",
                textDecoration: "none",
                color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                background: isActive ? "rgba(139, 92, 246, 0.15)" : "transparent",
                border: isActive ? "1px solid rgba(139, 92, 246, 0.25)" : "1px solid transparent",
                fontWeight: isActive ? 600 : 500,
              }}
              className={isActive ? "" : "glass-panel-hover"}
            >
              <Icon size={18} style={{ color: isActive ? "var(--primary)" : "inherit" }} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div style={{ padding: "20px 16px", borderTop: "1px solid var(--glass-border)", display: "flex", flexDirection: "column", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", padding: "0 8px" }}>
          <div style={{ width: "36px", height: "36px", borderRadius: "50%", background: "linear-gradient(135deg, var(--primary) 0%, #7c3aed 100%)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, color: "#fff" }}>
            {user?.full_name?.charAt(0).toUpperCase() || "ש"}
          </div>
          <div style={{ overflow: "hidden" }}>
            <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {user?.full_name || "משתמש"}
            </div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {user?.email}
            </div>
          </div>
        </div>
        <button
          onClick={logoutUser}
          style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 16px", borderRadius: "var(--border-radius)", background: "transparent", border: "none", color: "var(--danger)", cursor: "pointer", width: "100%", textAlign: "right", fontFamily: "inherit", fontSize: "0.875rem", fontWeight: 500 }}
          className="glass-panel-hover"
        >
          <LogOut size={18} />
          <span>יציאה והתחברות מחדש</span>
        </button>
      </div>
    </aside>
  );
}
