import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div style={{ minHeight: "100vh", background: "var(--background)" }}>
      <Sidebar />
      <Header />
      <main
        style={{
          marginRight: "var(--sidebar-width)",
          paddingTop: "var(--header-height)",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ flex: 1, padding: "40px" }}>{children}</div>
      </main>
    </div>
  );
}
