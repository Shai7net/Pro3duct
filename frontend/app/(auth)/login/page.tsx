"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { login } from "@/lib/api";
import { useAuth } from "@/components/providers/AuthProvider";
import { useToast } from "@/components/ui/Toast";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const { toast } = useToast();
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return toast("צריך למלא את כל השדות", "error");
    setLoading(true);
    try { const res = await login(email, password); toast("הכניסה הצליחה", "success"); await loginUser(res.access_token); }
    catch (err: any) { toast(err.detail || "כתובת האימייל או הסיסמה שגויות", "error"); }
    finally { setLoading(false); }
  };
  return <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", padding: "20px", background: "radial-gradient(circle at center,#100f24 0%,#080810 100%)" }}>
    <div style={{ maxWidth: "420px", width: "100%" }}>
      <div style={{ textAlign: "center", marginBottom: "32px" }}><span style={{ color: "var(--primary)", fontWeight: 900, marginLeft: "8px" }}>P3</span><span style={{ fontSize: "1.75rem", fontWeight: 800 }}>Pro3duct</span></div>
      <Card hoverEffect><CardHeader><CardTitle>כניסה ליישום</CardTitle><CardDescription>הזן את פרטי המשתמש שלך.</CardDescription></CardHeader><CardContent>
        <form onSubmit={handleSubmit}><Input label="כתובת אימייל" type="email" placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required /><Input label="סיסמה" type="password" placeholder="הזן סיסמה" value={password} onChange={(e) => setPassword(e.target.value)} required /><Button type="submit" variant="primary" fullWidth disabled={loading}>{loading ? "נכנס..." : "כניסה"}</Button></form>
        <div style={{ marginTop: "24px", textAlign: "center", fontSize: "0.875rem", color: "var(--text-secondary)" }}>אין לך חשבון? <Link href="/register" style={{ color: "var(--primary)" }}>הרשמה</Link></div>
      </CardContent></Card>
    </div>
  </div>;
}
