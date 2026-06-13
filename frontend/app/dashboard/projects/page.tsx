"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Search, FolderOpen, Calendar } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { listProjects, ProjectResponse } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { formatDateHe, heLabel } from "@/lib/hebrew";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const loadProjects = (query?: string) => {
    setLoading(true);
    listProjects(1, query).then((res) => setProjects(res.items)).catch(console.error).finally(() => setLoading(false));
  };
  useEffect(() => loadProjects(), []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800 }}>הפרויקטים שלי</h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "4px" }}>כאן אפשר לפתוח פרויקט, לעקוב אחר ההתקדמות ולהיכנס לעורך.</p>
        </div>
        <Link href="/dashboard/projects/new"><Button variant="primary"><Plus size={16} />פרויקט חדש</Button></Link>
      </div>

      <div className="glass-panel" style={{ padding: "16px 20px", display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{ position: "relative", flex: 1 }}>
          <Search size={18} style={{ position: "absolute", right: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
          <input type="text" placeholder="חיפוש לפי שם, מותג או דגם..." value={search} onChange={(e) => { setSearch(e.target.value); loadProjects(e.target.value); }} style={{ width: "100%", padding: "12px 42px 12px 16px", background: "rgba(255,255,255,.03)", border: "1px solid var(--glass-border)", borderRadius: "var(--border-radius)", color: "var(--text-primary)", fontFamily: "inherit" }} />
        </div>
      </div>

      {loading ? <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(320px,1fr))", gap: "24px" }}><Skeleton height={220} /><Skeleton height={220} /></div> : projects.length === 0 ? (
        <div style={{ textAlign: "center", padding: "80px 24px", background: "var(--glass-bg)", border: "1px solid var(--glass-border)", borderRadius: "var(--border-radius)", color: "var(--text-secondary)" }}>
          <FolderOpen size={48} style={{ marginBottom: "16px" }} /><h3>לא נמצאו פרויקטים</h3><p style={{ marginTop: "8px" }}>אפשר לשנות את החיפוש או ליצור פרויקט חדש.</p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(320px,1fr))", gap: "24px" }}>
          {projects.map((project) => (
            <Card key={project.id} hoverEffect>
              <CardHeader>
                <div style={{ display: "flex", justifyContent: "space-between" }}><Badge variant={["review","published"].includes(project.status) ? "success" : project.status === "generating" ? "warning" : "info"}>{heLabel(project.status)}</Badge><span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{heLabel(project.category)}</span></div>
                <CardTitle style={{ marginTop: "12px" }}><Link href={`/dashboard/projects/${project.id}`} style={{ textDecoration: "none", color: "inherit" }}>{project.name}</Link></CardTitle>
                <CardDescription>{project.description || "לא נוסף תיאור לפרויקט."}</CardDescription>
              </CardHeader>
              <CardContent>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-secondary)", fontSize: "0.85rem" }}><Calendar size={14} /><span>נוצר בתאריך: {formatDateHe(project.created_at)}</span></div>
                {project.brand && <div style={{ color: "var(--text-secondary)", marginTop: "10px" }}><strong>מותג:</strong> {project.brand}</div>}
              </CardContent>
              <div style={{ padding: "16px 20px", borderTop: "1px solid var(--glass-border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}><span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{project.asset_count} קבצים</span><Link href={`/dashboard/projects/${project.id}`}><Button variant="secondary" size="sm">פתיחת הפרויקט</Button></Link></div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
