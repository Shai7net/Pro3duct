"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { FolderKanban, Plus, Layers, ShieldCheck, Zap, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { getGenerationCapabilities, GenerationCapabilities, listProjects, ProjectResponse } from "@/lib/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { heLabel } from "@/lib/hebrew";

export default function DashboardOverview() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [capabilities, setCapabilities] = useState<GenerationCapabilities | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProjects().then((res) => setProjects(res.items)).catch(console.error).finally(() => setLoading(false));
    getGenerationCapabilities().then(setCapabilities).catch(() => setCapabilities(null));
  }, []);

  const activeJobs = projects.filter((p) => p.status === "generating").length;
  const readyTwins = projects.filter((p) => ["review", "published"].includes(p.status)).length;
  const realGenerationReady = capabilities?.real_3d_enabled === true;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-primary)" }}>
            שלום {user?.full_name?.split(" ")[0] || "שי"}
          </h1>
          <p style={{ color: "var(--text-secondary)", marginTop: "4px" }}>מכאן יוצרים ומנהלים את המודלים האינטראקטיביים שלך.</p>
        </div>
        <Link href="/dashboard/projects/new" style={{ textDecoration: "none" }}>
          <Button variant="primary"><Plus size={16} />יצירת פרויקט חדש</Button>
        </Link>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "24px" }}>
        {[
          { label: "כל הפרויקטים", value: projects.length, icon: FolderKanban, color: "var(--primary)" },
          { label: "מודלים בתהליך", value: activeJobs, icon: Zap, color: "var(--secondary)" },
          { label: "מודלים מוכנים", value: readyTwins, icon: Layers, color: "var(--info)" },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label} hoverEffect>
            <CardContent style={{ display: "flex", alignItems: "center", gap: "20px", padding: "24px" }}>
              <div style={{ background: "rgba(139,92,246,.1)", padding: "16px", borderRadius: "var(--border-radius)", color }}><Icon size={24} /></div>
              <div>
                <div style={{ fontSize: "0.875rem", color: "var(--text-secondary)" }}>{label}</div>
                <div style={{ fontSize: "2rem", fontWeight: 800, marginTop: "4px" }}>{loading ? <Skeleton width={50} height={36} /> : value}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "32px" }}>
        <Card>
          <CardHeader><CardTitle>פרויקטים אחרונים</CardTitle><CardDescription>גישה מהירה לעבודות האחרונות שלך.</CardDescription></CardHeader>
          <CardContent>
            {loading ? <Skeleton height={160} /> : projects.length === 0 ? (
              <div style={{ textAlign: "center", padding: "48px 24px", color: "var(--text-secondary)" }}>
                <FolderKanban size={42} style={{ marginBottom: "14px" }} />
                <h3>עדיין אין פרויקטים</h3>
                <p style={{ fontSize: "0.875rem", margin: "8px 0 20px" }}>צור פרויקט, העלה תמונות והפעל את תהליך היצירה.</p>
                <Link href="/dashboard/projects/new"><Button variant="secondary" size="sm">מתחילים עכשיו</Button></Link>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {projects.slice(0, 5).map((project) => (
                  <div key={project.id} className="glass-panel" style={{ padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                      <Link href={`/dashboard/projects/${project.id}`} style={{ fontWeight: 700, color: "var(--text-primary)", textDecoration: "none" }}>{project.name}</Link>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "4px" }}>קטגוריה: {heLabel(project.category)} · {project.asset_count} קבצים</div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                      <Badge variant={["review", "published"].includes(project.status) ? "success" : project.status === "generating" ? "warning" : "info"}>{heLabel(project.status)}</Badge>
                      <Link href={`/dashboard/projects/${project.id}`}><Button variant="ghost" size="sm">פתיחה</Button></Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>חשוב לדעת</CardTitle><CardDescription>מצב היכולות הנוכחי של המערכת.</CardDescription></CardHeader>
          <CardContent style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div style={{ display: "flex", gap: "12px" }}><ShieldCheck size={20} style={{ color: "var(--secondary)", flexShrink: 0 }} /><p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>הפרויקטים והקבצים שלך נשמרים בסביבת העבודה המקומית.</p></div>
            <div style={{ display: "flex", gap: "12px" }}><Info size={20} style={{ color: realGenerationReady ? "var(--success)" : "var(--warning)", flexShrink: 0 }} /><p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{realGenerationReady ? "יצירת 3D אמיתית פעילה: תמונות הפרויקט יישלחו ל-Meshy ויחזרו כקובץ GLB אינטראקטיבי." : "כדי ליצור מודל אמיתי מהתמונות צריך לחבר מפתח Meshy במסך הגדרות וחיבורי AI. בלי מפתח, היצירה תיעצר במקום ליצור דמו מזויף."}</p></div>
            <Link href="/dashboard/settings"><Button variant="secondary" size="sm" fullWidth>הגדרות וחיבורי AI</Button></Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
