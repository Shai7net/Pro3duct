"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Save, ShieldAlert, CheckSquare, Sparkles, Send } from "lucide-react";
import { useEditorStore } from "@/lib/stores/editorStore";
import { getDigitalTwinByProject, updateDigitalTwin, validateDigitalTwin, publishDigitalTwin, ValidationResponse } from "@/lib/api";
import SceneCanvas from "./SceneCanvas";
import ProductViewer from "./ProductViewer";
import { HierarchyPanel, MaterialPanel, InteractionsPanel, LightingPanel, StatesPanel } from "./EditorPanels";
import { Button } from "@/components/ui/Button";
import { Tabs } from "@/components/ui/Tabs";
import { useToast } from "@/components/ui/Toast";
import { Dialog } from "@/components/ui/Dialog";
import { Badge } from "@/components/ui/Badge";

export default function EditorScene() {
  const params = useParams();
  const projectId = params.id as string;
  const { toast } = useToast();
  const router = useRouter();

  const spec = useEditorStore((state) => state.spec);
  const setSpec = useEditorStore((state) => state.setSpec);
  const activeTab = useEditorStore((state) => state.activeTab);
  const setActiveTab = useEditorStore((state) => state.setActiveTab);

  const [twinId, setTwinId] = useState<string | null>(null);
  const [glbUrl, setGlbUrl] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [publishing, setPublishing] = useState(false);

  // Dialogs
  const [valResults, setValResults] = useState<ValidationResponse | null>(null);
  const [showValDialog, setShowValDialog] = useState(false);
  const [pubResults, setPubResults] = useState<{ publish_url: string; embed_code: string } | null>(null);
  const [showPubDialog, setShowPubDialog] = useState(false);

  useEffect(() => {
    // Resolve digital twin for this project on load
    getDigitalTwinByProject(projectId)
      .then((res) => {
        setTwinId(res.id);
        setGlbUrl(res.glb_url);
        if (res.spec) {
          setSpec(res.spec);
        }
      })
      .catch(() => {
        toast("המודל עדיין לא מוכן לעריכה", "error");
        router.push(`/dashboard/projects/${projectId}`);
      });
  }, [projectId]);

  const handleSave = async () => {
    if (!twinId || !spec) return;

    setSaving(true);
    try {
      await updateDigitalTwin(twinId, spec);
      toast("השינויים נשמרו", "success");
    } catch (err: any) {
      toast("שמירת השינויים נכשלה", "error");
    } finally {
      setSaving(false);
    }
  };

  const handleValidate = async () => {
    if (!twinId) return;

    setValidating(true);
    try {
      const res = await validateDigitalTwin(twinId);
      setValResults(res);
      setShowValDialog(true);
      if (res.is_valid) {
        toast("בדיקת המודל הסתיימה בהצלחה", "success");
      } else {
        toast("נמצאו אזהרות שכדאי לבדוק", "warning");
      }
    } catch (err: any) {
      toast("בדיקת המודל נכשלה", "error");
    } finally {
      setValidating(false);
    }
  };

  const handlePublish = async () => {
    if (!twinId) return;

    setPublishing(true);
    try {
      // Perform validation check first
      const val = await validateDigitalTwin(twinId);
      if (val.errors.length > 0) {
        toast("לא ניתן לפרסם לפני תיקון השגיאות", "error");
        setValResults(val);
        setShowValDialog(true);
        return;
      }

      const res = await publishDigitalTwin(twinId);
      setPubResults(res);
      setShowPubDialog(true);
      toast("המודל פורסם בהצלחה", "success");
    } catch (err: any) {
      toast(err.detail || "הפרסום נכשל", "error");
    } finally {
      setPublishing(false);
    }
  };

  const editorTabs = [
    { id: "hierarchy", label: "חלקים" },
    { id: "materials", label: "חומרים" },
    { id: "interactions", label: "אינטראקציות" },
    { id: "lighting", label: "תאורה" },
    { id: "states", label: "מצבי פעולה" },
  ] as const;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        background: "#080810",
        color: "#fff",
        overflow: "hidden",
      }}
    >
      {/* Visual Editor Header Controls */}
      <header
        style={{
          height: "64px",
          background: "rgba(10, 11, 26, 0.9)",
          borderBottom: "1px solid var(--glass-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <Link
            href={`/dashboard/projects/${projectId}`}
            style={{
              color: "var(--text-secondary)",
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "0.9rem",
            }}
            className="hover-glow"
          >
            <ArrowLeft size={16} /> יציאה מהעורך
          </Link>
          <div
            style={{ width: "1px", height: "20px", background: "var(--glass-border)" }}
          />
          <h2 style={{ fontSize: "1.1rem", fontWeight: 800 }}>עורך תלת־ממד אינטראקטיבי</h2>
        </div>

        <div style={{ display: "flex", gap: "12px" }}>
          <Button variant="secondary" size="sm" onClick={handleSave} disabled={saving}>
            <Save size={14} />
            {saving ? "שומר..." : "שמירת שינויים"}
          </Button>

          <Button variant="secondary" size="sm" onClick={handleValidate} disabled={validating}>
            <ShieldAlert size={14} />
            {validating ? "בודק..." : "בדיקת המודל"}
          </Button>

          <Button variant="primary" size="sm" onClick={handlePublish} disabled={publishing}>
            <Send size={14} />
            {publishing ? "מפרסם..." : "פרסום המודל"}
          </Button>
        </div>
      </header>

      {/* Main workspace layout */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* Left: 3D canvas viewport */}
        <div style={{ flex: 1, position: "relative", height: "100%" }}>
          <SceneCanvas>
            <ProductViewer glbUrl={glbUrl} />
          </SceneCanvas>
        </div>

        {/* Right: Property Inspector Sidebar */}
        <div
          style={{
            width: "380px",
            background: "rgba(10, 11, 26, 0.95)",
            borderRight: "1px solid var(--glass-border)",
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
            zIndex: 5,
          }}
        >
          <div style={{ padding: "20px", borderBottom: "1px solid var(--glass-border)" }}>
            <Tabs
              tabs={editorTabs as any}
              activeTab={activeTab}
              onChange={(id) => setActiveTab(id as any)}
              className="editor-tabs"
            />
          </div>

          <div style={{ padding: "24px", flex: 1 }}>
            {activeTab === "hierarchy" && <HierarchyPanel />}
            {activeTab === "materials" && <MaterialPanel />}
            {activeTab === "interactions" && <InteractionsPanel />}
            {activeTab === "lighting" && <LightingPanel />}
            {activeTab === "states" && <StatesPanel />}
          </div>
        </div>
      </div>

      {/* Validation Results Dialog */}
      <Dialog
        isOpen={showValDialog}
        onClose={() => setShowValDialog(false)}
        title="בדיקת איכות ואינטראקציות"
      >
        {valResults && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>ציון איכות:</span>
              <Badge variant={valResults.is_valid ? "success" : "danger"}>
                {Math.round(valResults.quality_score * 100)}%
              </Badge>
            </div>

            <div>
              <h4 style={{ fontSize: "0.9rem", color: "var(--text-primary)", marginBottom: "8px" }}>שגיאות</h4>
              {valResults.errors.length === 0 ? (
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>לא נמצאו שגיאות קריטיות.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {valResults.errors.map((e, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "8px 12px",
                        background: "rgba(239, 68, 68, 0.1)",
                        border: "1px solid rgba(239, 68, 68, 0.2)",
                        color: "var(--danger)",
                        fontSize: "0.8rem",
                        borderRadius: "4px",
                      }}
                    >
                      [{e.code}] {e.message}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h4 style={{ fontSize: "0.9rem", color: "var(--text-primary)", marginBottom: "8px" }}>אזהרות</h4>
              {valResults.warnings.length === 0 ? (
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>לא נמצאו אזהרות.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {valResults.warnings.map((w, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "8px 12px",
                        background: "rgba(245, 158, 11, 0.1)",
                        border: "1px solid rgba(245, 158, 11, 0.2)",
                        color: "var(--warning)",
                        fontSize: "0.8rem",
                        borderRadius: "4px",
                      }}
                    >
                      [{w.code}] {w.message}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "12px" }}>
              <Button variant="secondary" onClick={() => setShowValDialog(false)}>
                סגירה
              </Button>
            </div>
          </div>
        )}
      </Dialog>

      {/* Publish Embed Dialog */}
      <Dialog
        isOpen={showPubDialog}
        onClose={() => setShowPubDialog(false)}
        title="פרסום המודל האינטראקטיבי"
      >
        {pubResults && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              המודל פורסם. אפשר לפתוח אותו בקישור או להטמיע אותו באתר.
            </p>

            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                קישור ציבורי
              </label>
              <input
                type="text"
                readOnly
                value={pubResults.publish_url}
                onClick={(e) => {
                  (e.target as any).select();
                  navigator.clipboard.writeText(pubResults.publish_url);
                  toast("הקישור הועתק", "success");
                }}
                style={{
                  width: "100%",
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid var(--glass-border)",
                  borderRadius: "var(--border-radius)",
                  padding: "10px 14px",
                  color: "#fff",
                  fontSize: "0.85rem",
                  cursor: "copy",
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                קוד הטמעה לאתר
              </label>
              <textarea
                readOnly
                value={pubResults.embed_code}
                onClick={(e) => {
                  (e.target as any).select();
                  navigator.clipboard.writeText(pubResults.embed_code);
                  toast("הקוד הועתק", "success");
                }}
                style={{
                  width: "100%",
                  height: "80px",
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid var(--glass-border)",
                  borderRadius: "var(--border-radius)",
                  padding: "10px 14px",
                  color: "#fff",
                  fontSize: "0.85rem",
                  fontFamily: "monospace",
                  cursor: "copy",
                  resize: "none",
                }}
              />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px" }}>
              <Button variant="secondary" onClick={() => setShowPubDialog(false)}>
                סגירה
              </Button>
              <Link href={`/embed/${twinId}`} target="_blank" style={{ textDecoration: "none" }}>
                <Button variant="primary">
                  פתיחת התצוגה
                </Button>
              </Link>
            </div>
          </div>
        )}
      </Dialog>
    </div>
  );
}
