"use client";

import React, { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Upload,
  Play,
  Cpu,
  Layers,
  CheckCircle,
  FileCode,
  Image as ImageIcon,
  Ruler,
  AlertTriangle,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Progress } from "@/components/ui/Progress";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  getProject,
  listAssets,
  uploadAssets,
  startGeneration,
  getJobStatus,
  getDigitalTwinByProject,
  getGenerationCapabilities,
  ProjectResponse,
  AssetResponse,
  JobResponse,
  DigitalTwinResponse,
  GenerationCapabilities,
} from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { heLabel } from "@/lib/hebrew";

export default function ProjectDetailsPage() {
  const params = useParams();
  const projectId = params.id as string;
  const { toast } = useToast();

  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [assets, setAssets] = useState<AssetResponse[]>([]);
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwinResponse | null>(null);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [capabilities, setCapabilities] = useState<GenerationCapabilities | null>(null);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [startingGen, setStartingGen] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadAllData = async () => {
    try {
      const projData = await getProject(projectId);
      setProject(projData);
      getGenerationCapabilities().then(setCapabilities).catch(() => setCapabilities(null));

      const assetsData = await listAssets(projectId);
      setAssets(assetsData);

      // Fetch twin details after the generation workflow creates one.
      if (["review", "published"].includes(projData.status)) {
        try {
          const twinData = await getDigitalTwinByProject(projectId);
          setDigitalTwin(twinData);
        } catch {}
      }
    } catch (err: any) {
      toast("לא ניתן לטעון את פרטי הפרויקט", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [projectId]);

  // Poll for project and job updates while generation is running.
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (project?.status === "generating") {
      interval = setInterval(async () => {
        try {
          const projData = await getProject(projectId);
          setProject(projData);
          if (job) {
            setJob(await getJobStatus(job.id));
          }

          if (projData.status !== "generating") {
            clearInterval(interval);
            loadAllData();
            toast("תהליך היצירה הסתיים", "success");
          }
        } catch {}
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [project?.status]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      const fileList = Array.from(files);
      await uploadAssets(projectId, fileList);
      toast("התמונות הועלו בהצלחה", "success");
      const assetsData = await listAssets(projectId);
      setAssets(assetsData);
      // Update asset count in project
      if (project) {
        setProject({
          ...project,
          asset_count: project.asset_count + fileList.length,
        });
      }
    } catch (err: any) {
      toast(err.detail || "העלאת התמונות נכשלה", "error");
    } finally {
      setUploading(false);
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  const handleStartGeneration = async () => {
    if (assets.length === 0) {
      toast("צריך להעלות לפחות תמונה אחת לפני שמתחילים", "error");
      return;
    }

    setStartingGen(true);
    try {
      const jobData = await startGeneration(projectId);
      setJob(jobData);
      toast("תהליך יצירת המודל התחיל", "success");
      if (project) {
        setProject({
          ...project,
          status: "generating",
        });
      }
    } catch (err: any) {
      toast(err.detail || "לא ניתן להתחיל את יצירת המודל", "error");
    } finally {
      setStartingGen(false);
    }
  };

  const realGenerationReady = capabilities?.real_3d_enabled === true;

  if (loading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        <Skeleton height={40} width={200} />
        <Skeleton height={200} />
        <Skeleton height={300} />
      </div>
    );
  }

  if (!project) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <AlertTriangle size={48} style={{ color: "var(--danger)" }} />
        <h2>הפרויקט לא נמצא</h2>
        <Link href="/dashboard/projects">חזרה לפרויקטים</Link>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
      {/* Back navigation */}
      <div>
        <Link
          href="/dashboard/projects"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            color: "var(--text-secondary)",
            textDecoration: "none",
            fontSize: "0.9rem",
          }}
          className="hover-glow"
        >
          <ArrowLeft size={16} />
          חזרה לפרויקטים
        </Link>
      </div>

      {/* Header and Core Operations */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text-primary)" }}>{project.name}</h1>
            <Badge
              variant={
                ["review", "published"].includes(project.status)
                  ? "success"
                  : project.status === "generating"
                  ? "warning"
                  : "info"
              }
            >
              {heLabel(project.status)}
            </Badge>
          </div>
          <p style={{ color: "var(--text-secondary)", marginTop: "4px" }}>{project.description}</p>
        </div>

        <div style={{ display: "flex", gap: "12px" }}>
          {project.status === "draft" && (
            <Button variant="primary" onClick={handleStartGeneration} disabled={startingGen}>
              <Play size={16} />
              {startingGen ? "מתחיל..." : "התחלת יצירת המודל"}
            </Button>
          )}

          {["review", "published"].includes(project.status) && digitalTwin && (
            <Link href={`/dashboard/projects/${projectId}/editor`} style={{ textDecoration: "none" }}>
              <Button variant="primary">
                <Layers size={16} />
                פתיחת העורך האינטראקטיבי
              </Button>
            </Link>
          )}
        </div>
      </div>

      <div
        style={{
          padding: "14px 16px",
          border: realGenerationReady ? "1px solid rgba(34, 197, 94, 0.35)" : "1px solid rgba(245, 158, 11, 0.35)",
          borderRadius: "var(--border-radius)",
          background: realGenerationReady ? "rgba(34, 197, 94, 0.08)" : "rgba(245, 158, 11, 0.08)",
          color: "var(--text-secondary)",
          display: "flex",
          gap: "12px",
          alignItems: "flex-start",
        }}
      >
        {realGenerationReady ? (
          <CheckCircle size={18} style={{ color: "var(--success)", flexShrink: 0, marginTop: "2px" }} />
        ) : (
          <AlertTriangle size={18} style={{ color: "var(--warning)", flexShrink: 0, marginTop: "2px" }} />
        )}
        <div style={{ fontSize: "0.85rem", lineHeight: 1.55 }}>
          <strong style={{ color: "var(--text-primary)" }}>
            {realGenerationReady ? "יצירת 3D אמיתית פעילה:" : "נדרש חיבור AI:"}
          </strong>{" "}
          {realGenerationReady
            ? "המערכת תשלח עד 4 תמונות מוצר ל-Meshy, תיצור GLB אמיתי, תשמור אותו מקומית ותפתח אותו בעורך האינטראקטיבי."
            : "כדי ליצור מודל אמיתי מהתמונות צריך להוסיף מפתח Meshy במסך הגדרות וחיבורי AI או להגדיר MESHY_API_KEY בקובץ .env. בלי מפתח לא ייווצר דמו מזויף."}
        </div>
      </div>

      {/* Grid details */}
      <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: "32px" }}>
        {/* Left column: Pipeline progress monitor or image uploads */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* If generating, show status bar */}
          {project.status === "generating" && (
            <Card className="glow-active">
              <CardHeader>
                <CardTitle>יצירת המודל מתבצעת כעת</CardTitle>
                <CardDescription>המערכת מעבדת את הקבצים ומכינה את המודל לבדיקה.</CardDescription>
              </CardHeader>
              <CardContent>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px", fontSize: "0.9rem" }}>
                  <span>התקדמות התהליך</span>
                  <span>{job?.progress_percent ?? 0}%</span>
                </div>
                <Progress value={job?.progress_percent ?? 0} />

                <div
                  style={{
                    marginTop: "20px",
                    background: "rgba(255,255,255,0.02)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "var(--border-radius)",
                    padding: "16px",
                  }}
                >
                  <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                    <Cpu size={16} style={{ color: "var(--primary)" }} />
                    <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                      שלב נוכחי: {job?.current_step || "מתחיל את תהליך היצירה..."}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upload and gallery */}
          <Card>
            <CardHeader style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <CardTitle>תמונות המקור</CardTitle>
                <CardDescription>מומלץ להעלות תמונות חדות של המוצר ממספר זוויות.</CardDescription>
              </div>
              {project.status === "draft" && (
                <>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    style={{ display: "none" }}
                  />
                  <Button variant="secondary" size="sm" onClick={triggerUpload} disabled={uploading}>
                    <Upload size={14} />
                    {uploading ? "מעלה תמונות..." : "העלאת תמונות"}
                  </Button>
                </>
              )}
            </CardHeader>
            <CardContent>
              {assets.length === 0 ? (
                <div
                  style={{
                    textAlign: "center",
                    padding: "48px 24px",
                    border: "1px dashed var(--glass-border)",
                    borderRadius: "var(--border-radius)",
                    color: "var(--text-muted)",
                  }}
                >
                  <ImageIcon size={36} style={{ marginBottom: "12px" }} />
                  <p>עדיין לא הועלו תמונות.</p>
                  {project.status === "draft" && (
                    <p style={{ fontSize: "0.8rem", marginTop: "4px" }}>
                      העלה בין 3 ל־20 תמונות איכותיות מזוויות שונות.
                    </p>
                  )}
                </div>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
                    gap: "16px",
                  }}
                >
                  {assets.map((asset) => (
                    <div
                      key={asset.id}
                      className="glass-panel"
                      style={{
                        padding: "10px",
                        textAlign: "center",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      <div
                        style={{
                          width: "100%",
                          height: "90px",
                          background: "rgba(255,255,255,0.03)",
                          borderRadius: "4px",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          color: "var(--text-muted)",
                          fontSize: "1.5rem",
                        }}
                      >
                        📸
                      </div>
                      <span
                        style={{
                          fontSize: "0.75rem",
                          color: "var(--text-primary)",
                          textOverflow: "ellipsis",
                          overflow: "hidden",
                          whiteSpace: "nowrap",
                          width: "100px",
                        }}
                        title={asset.original_filename}
                      >
                        {asset.original_filename}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right column: Physical details metadata */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <Card>
            <CardHeader>
              <CardTitle>פרטי המוצר</CardTitle>
              <CardDescription>המידות וההגדרות שהוזנו בעת יצירת הפרויקט.</CardDescription>
            </CardHeader>
            <CardContent style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <Ruler size={18} style={{ color: "var(--primary)" }} />
                <div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>מידות</div>
                  <div style={{ fontSize: "0.95rem", color: "var(--text-primary)", fontWeight: 600 }}>
                    {project.width_mm && project.height_mm && project.depth_mm ? (
                      `${project.width_mm} x ${project.height_mm} x ${project.depth_mm} mm`
                    ) : (
                      "לא צוינו"
                    )}
                  </div>
                </div>
              </div>

              <div style={{ borderTop: "1px solid var(--glass-border)", paddingTop: "12px" }}>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>קטגוריה</div>
                <div style={{ fontSize: "0.95rem", color: "var(--text-primary)", fontWeight: 600, textTransform: "capitalize" }}>
                  {heLabel(project.category)}
                </div>
              </div>

              <div style={{ borderTop: "1px solid var(--glass-border)", paddingTop: "12px" }}>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>רמת איכות</div>
                <div style={{ fontSize: "0.95rem", color: "var(--text-primary)", fontWeight: 600 }}>
                  {heLabel(project.quality_mode)}
                </div>
              </div>

              <div style={{ borderTop: "1px solid var(--glass-border)", paddingTop: "12px" }}>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>רמת פרטיות</div>
                <div style={{ fontSize: "0.95rem", color: "var(--text-primary)", fontWeight: 600 }}>
                  {heLabel(project.privacy_policy)}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Digital Twin Deliverables */}
          {digitalTwin && (
            <Card>
              <CardHeader>
                <CardTitle>קבצי המודל</CardTitle>
                <CardDescription>הקבצים שנוצרו בתהליך.</CardDescription>
              </CardHeader>
              <CardContent style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <div
                  className="glass-panel"
                  style={{
                    padding: "12px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <FileCode size={16} style={{ color: "var(--secondary)" }} />
                    <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>קובץ GLB לתצוגה באתר</span>
                  </div>
                  <Badge variant="success">מוכן</Badge>
                </div>

                <div
                  className="glass-panel"
                  style={{
                    padding: "12px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <FileCode size={16} style={{ color: "var(--info)" }} />
                    <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Apple USDZ (AR)</span>
                  </div>
                  <Badge variant="success">נוצר</Badge>
                </div>

                <div
                  className="glass-panel"
                  style={{
                    padding: "12px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <CheckCircle size={16} style={{ color: "var(--primary)" }} />
                    <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>חומרים וקובץ Blender</span>
                  </div>
                  <Badge variant="success">מוכן</Badge>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
