"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Save } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { createProject } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";

export default function NewProjectPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("electronics");
  const [qualityMode, setQualityMode] = useState("commercial");
  const [privacyPolicy, setPrivacyPolicy] = useState("standard");
  const [brand, setBrand] = useState("");
  const [modelNumber, setModelNumber] = useState("");
  const [widthMm, setWidthMm] = useState("");
  const [heightMm, setHeightMm] = useState("");
  const [depthMm, setDepthMm] = useState("");
  const [weightGrams, setWeightGrams] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return toast("צריך לתת שם לפרויקט", "error");
    setLoading(true);
    try {
      const res = await createProject({
        name,
        description: description || undefined,
        category,
        quality_mode: qualityMode,
        privacy_policy: privacyPolicy,
        brand: brand || undefined,
        model_number: modelNumber || undefined,
        width_mm: widthMm ? parseInt(widthMm) : undefined,
        height_mm: heightMm ? parseInt(heightMm) : undefined,
        depth_mm: depthMm ? parseInt(depthMm) : undefined,
        weight_grams: weightGrams ? parseInt(weightGrams) : undefined,
      });
      toast(`הפרויקט "${res.name}" נוצר בהצלחה`, "success");
      router.push(`/dashboard/projects/${res.id}`);
    } catch (err: any) {
      toast(err.detail || "יצירת הפרויקט נכשלה", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "32px", maxWidth: "800px", margin: "0 auto" }}>
      <Link href="/dashboard/projects" style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--text-secondary)", textDecoration: "none" }}><ArrowRight size={16} />חזרה לפרויקטים</Link>
      <div><h1 style={{ fontSize: "2rem", fontWeight: 800 }}>יצירת פרויקט חדש</h1><p style={{ color: "var(--text-secondary)", marginTop: "4px" }}>מלא את הפרטים הידועים לך. אפשר להשאיר שדות לא חשובים ריקים.</p></div>
      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <Card>
            <CardHeader><CardTitle>פרטי המוצר</CardTitle><CardDescription>השם והתיאור יעזרו לך לזהות את הפרויקט בהמשך.</CardDescription></CardHeader>
            <CardContent>
              <Input label="שם המוצר או הפרויקט *" placeholder="לדוגמה: שלט חכם" value={name} onChange={(e) => setName(e.target.value)} required />
              <Input label="תיאור קצר" placeholder="מהו המוצר ומה מיוחד בו?" value={description} onChange={(e) => setDescription(e.target.value)} />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <Select label="קטגוריה" value={category} onChange={(e) => setCategory(e.target.value)} options={[
                  { value: "electronics", label: "אלקטרוניקה" }, { value: "appliance", label: "מכשירי חשמל" }, { value: "furniture", label: "ריהוט ועיצוב" }, { value: "packaging", label: "אריזות" }, { value: "industrial", label: "ציוד תעשייתי" }, { value: "automotive", label: "רכב" }, { value: "fashion", label: "אופנה" }, { value: "other", label: "אחר" },
                ]} />
                <Select label="רמת איכות" value={qualityMode} onChange={(e) => setQualityMode(e.target.value)} options={[
                  { value: "commercial", label: "מסחרית - מתאימה לתצוגה באתר" }, { value: "engineering", label: "הנדסית - דיוק גבוה יותר" },
                ]} />
              </div>
              <Select label="רמת פרטיות" value={privacyPolicy} onChange={(e) => setPrivacyPolicy(e.target.value)} options={[
                { value: "standard", label: "רגילה - שימוש בספקים שהוגדרו" }, { value: "restricted", label: "מוגבלת - ספקים מאושרים בלבד" }, { value: "private", label: "פרטית - עיבוד מקומי בלבד" },
              ]} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>מידות ופרטים נוספים</CardTitle><CardDescription>מידות מדויקות עוזרות לקבוע את קנה המידה של המודל.</CardDescription></CardHeader>
            <CardContent>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}><Input label="מותג" placeholder="לדוגמה: Samsung" value={brand} onChange={(e) => setBrand(e.target.value)} /><Input label="מספר דגם" placeholder="לדוגמה: BT-500" value={modelNumber} onChange={(e) => setModelNumber(e.target.value)} /></div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: "12px" }}><Input label="רוחב במ״מ" type="number" value={widthMm} onChange={(e) => setWidthMm(e.target.value)} /><Input label="גובה במ״מ" type="number" value={heightMm} onChange={(e) => setHeightMm(e.target.value)} /><Input label="עומק במ״מ" type="number" value={depthMm} onChange={(e) => setDepthMm(e.target.value)} /><Input label="משקל בגרם" type="number" value={weightGrams} onChange={(e) => setWeightGrams(e.target.value)} /></div>
            </CardContent>
          </Card>
          <div style={{ display: "flex", justifyContent: "flex-start", gap: "16px" }}><Button type="submit" variant="primary" disabled={loading}><Save size={16} />{loading ? "יוצר את הפרויקט..." : "יצירת הפרויקט"}</Button><Link href="/dashboard/projects"><Button type="button" variant="ghost">ביטול</Button></Link></div>
        </div>
      </form>
    </div>
  );
}
