"use client";

import React from "react";
import dynamic from "next/dynamic";

// Disable SSR for 3D webgl editor to prevent document is not defined error on Next.js server compile.
const EditorScene = dynamic(() => import("@/components/three/EditorScene"), {
  ssr: false,
});

export default function EditorPage() {
  return <EditorScene />;
}
