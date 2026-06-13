"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { getPublicDigitalTwin, DigitalTwinResponse } from "@/lib/api";
import { useEditorStore } from "@/lib/stores/editorStore";

const SceneCanvas = dynamic(() => import("@/components/three/SceneCanvas"), { ssr: false });
const ProductViewer = dynamic(() => import("@/components/three/ProductViewer"), { ssr: false });

export default function PublicEmbedPage() {
  const twinId = useParams().id as string;
  const setSpec = useEditorStore((state) => state.setSpec);
  const [twin, setTwin] = useState<DigitalTwinResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getPublicDigitalTwin(twinId).then((res) => { setTwin(res); if (res.spec) setSpec(res.spec); }).catch(() => setError(true)).finally(() => setLoading(false));
  }, [twinId, setSpec]);

  if (loading) return <div style={{ width: "100vw", height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#080810", color: "var(--text-secondary)" }}>טוען את המודל האינטראקטיבי...</div>;
  if (error || !twin) return <div style={{ width: "100vw", height: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#080810", color: "var(--danger)" }}>לא ניתן לטעון את המודל.</div>;

  return <div style={{ width: "100vw", height: "100vh", position: "relative", overflow: "hidden" }}>
    <SceneCanvas><ProductViewer glbUrl={twin.glb_url} /></SceneCanvas>
    <div style={{ position: "absolute", bottom: "24px", right: "24px", pointerEvents: "none", background: "rgba(10,11,26,.75)", backdropFilter: "blur(8px)", border: "1px solid var(--glass-border)", padding: "16px 20px", borderRadius: "var(--border-radius)", maxWidth: "340px" }}>
      <h3 style={{ fontSize: "1rem", fontWeight: 700 }}>{twin.spec?.product_name || "מודל אינטראקטיבי"}</h3>
      {twin.spec?.brand && <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginTop: "4px" }}>מותג: {twin.spec.brand}</p>}
      <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "8px" }}>גרור כדי לסובב, גלול כדי להתקרב ולחץ על חלקים אינטראקטיביים.</p>
    </div>
    <div style={{ position: "absolute", top: "16px", left: "24px", color: "var(--text-muted)", fontSize: "0.75rem" }}>נוצר באמצעות <strong>Pro3duct</strong></div>
  </div>;
}
