"use client";

import React, { useEffect, useState } from "react";
import { Plus, Trash2, Key, Shield, Info } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Tabs } from "@/components/ui/Tabs";
import { listSystemProviders, listCredentials, addCredential, deleteCredential, SystemProviderResponse, ProviderCredentialResponse } from "@/lib/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { useToast } from "@/components/ui/Toast";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";

export default function SettingsPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("account");
  const [providers, setProviders] = useState<SystemProviderResponse[]>([]);
  const [credentials, setCredentials] = useState<ProviderCredentialResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [label, setLabel] = useState("");

  useEffect(() => {
    if (activeTab !== "providers") return;
    setLoading(true);
    Promise.all([listSystemProviders(), listCredentials()])
      .then(([sys, creds]) => { setProviders(sys); setCredentials(creds); if (sys[0]) setSelectedProvider(sys[0].name); })
      .catch(() => toast("לא ניתן לטעון את רשימת ספקי ה־AI", "error"))
      .finally(() => setLoading(false));
  }, [activeTab, toast]);

  const addKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey || !label) return toast("צריך להזין מפתח API ותיאור קצר", "error");
    try {
      const res = await addCredential(selectedProvider, apiKey, label);
      setCredentials((prev) => [...prev, res]); setApiKey(""); setLabel("");
      toast("המפתח נשמר בצורה מוצפנת", "success");
    } catch (err: any) { toast(err.detail || "שמירת המפתח נכשלה", "error"); }
  };

  const removeKey = async (id: string) => {
    if (!confirm("למחוק את מפתח ה־API הזה?")) return;
    try { await deleteCredential(id); setCredentials((prev) => prev.filter((c) => c.id !== id)); toast("המפתח נמחק", "success"); }
    catch { toast("מחיקת המפתח נכשלה", "error"); }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px", maxWidth: "900px" }}>
      <div><h1 style={{ fontSize: "2rem", fontWeight: 800 }}>הגדרות</h1><p style={{ color: "var(--text-secondary)", marginTop: "4px" }}>פרטי החשבון, חיבורי AI והרשאות סביבת העבודה.</p></div>
      <Tabs tabs={[{ id: "account", label: "החשבון שלי" }, { id: "providers", label: "חיבורי AI" }, { id: "team", label: "משתמשים" }]} activeTab={activeTab} onChange={setActiveTab} />

      {activeTab === "account" && <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        <Card><CardHeader><CardTitle>פרטי המשתמש</CardTitle><CardDescription>פרטי הכניסה הפעילים כרגע.</CardDescription></CardHeader><CardContent>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}><Input label="שם מלא" value={user?.full_name || ""} readOnly /><Input label="כתובת אימייל" value={user?.email || ""} readOnly /></div>
        </CardContent></Card>
        <Card><CardHeader><CardTitle>סביבת העבודה המקומית</CardTitle><CardDescription>הנתונים והקבצים נשמרים תחת סביבת העבודה שלך.</CardDescription></CardHeader><CardContent><div style={{ display: "flex", gap: "12px", alignItems: "center" }}><Shield size={20} style={{ color: "var(--secondary)" }} /><span>מזהה סביבת עבודה: <code dir="ltr">{user?.tenant_id || "מקומי"}</code></span></div></CardContent></Card>
      </div>}

      {activeTab === "providers" && <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
        <div className="glass-panel" style={{ padding: "16px 20px", display: "flex", gap: "12px" }}><Key size={20} style={{ color: "var(--primary)", flexShrink: 0 }} /><div><h4>חיבור שירותי AI חיצוניים</h4><p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "4px" }}>כדי ליצור מודל אמיתי מתמונות יהיה צורך להשלים חיבור לספק מתאים. המפתחות נשמרים מוצפנים.</p></div></div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          <Card><CardHeader><CardTitle>הוספת מפתח API</CardTitle><CardDescription>הזן מפתח מספק AI חיצוני.</CardDescription></CardHeader><CardContent>{loading ? <Skeleton height={180} /> : <form onSubmit={addKey}>
            <Select label="בחירת ספק" value={selectedProvider} onChange={(e) => setSelectedProvider(e.target.value)} options={providers.map((p) => ({ value: p.name, label: p.display_name }))} />
            <Input label="תיאור המפתח" placeholder="לדוגמה: המפתח האישי שלי" value={label} onChange={(e) => setLabel(e.target.value)} required />
            <Input label="מפתח API" type="password" placeholder="הדבק כאן את המפתח" value={apiKey} onChange={(e) => setApiKey(e.target.value)} required />
            <Button type="submit" variant="primary" fullWidth><Plus size={16} />שמירת המפתח</Button>
          </form>}</CardContent></Card>
          <Card><CardHeader><CardTitle>מפתחות שמורים</CardTitle><CardDescription>המפתחות הפעילים בסביבת העבודה.</CardDescription></CardHeader><CardContent>{loading ? <Skeleton height={120} /> : credentials.length === 0 ? <div style={{ textAlign: "center", padding: "40px 16px", color: "var(--text-muted)" }}><Info size={32} style={{ marginBottom: "12px" }} /><p>עדיין לא נשמרו מפתחות.</p></div> : <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>{credentials.map((cred) => <div key={cred.id} className="glass-panel" style={{ padding: "12px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}><div><strong>{cred.label}</strong><div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>ספק: {cred.provider_name} · שימושים: {cred.total_requests}</div></div><Button variant="ghost" size="sm" onClick={() => removeKey(cred.id)}><Trash2 size={16} style={{ color: "var(--danger)" }} /></Button></div>)}</div>}</CardContent></Card>
        </div>
      </div>}

      {activeTab === "team" && <Card><CardHeader><CardTitle>משתמשים בסביבת העבודה</CardTitle><CardDescription>כרגע מוגדר משתמש מקומי יחיד.</CardDescription></CardHeader><CardContent><div className="glass-panel" style={{ padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center" }}><div><strong>{user?.full_name}</strong><div style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>{user?.email}</div></div><Badge variant="success">בעלים</Badge></div></CardContent></Card>}
    </div>
  );
}
