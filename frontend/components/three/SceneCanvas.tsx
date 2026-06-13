"use client";

import React, { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid, Stage } from "@react-three/drei";
import { useEditorStore } from "@/lib/stores/editorStore";

interface SceneCanvasProps {
  children: React.ReactNode;
}

export default function SceneCanvas({ children }: SceneCanvasProps) {
  const activeTab = useEditorStore((state) => state.activeTab);

  return (
    <div style={{ width: "100%", height: "100%", position: "relative" }}>
      <Canvas
        shadows
        camera={{ position: [0, 1.5, 3], fov: 45 }}
        style={{ background: "#0b0c1b" }}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.2} />

          <Stage
            intensity={0.6}
            environment="city"
            adjustCamera={false}
            shadows={{ type: "contact", opacity: 0.4, blur: 2 }}
          >
            {children}
          </Stage>

          {/* Grid helper for editor context */}
          {activeTab === "lighting" && (
            <Grid
              position={[0, -0.01, 0]}
              args={[10, 10]}
              cellSize={0.1}
              cellThickness={0.8}
              cellColor="#6b7280"
              sectionSize={1}
              sectionThickness={1.2}
              sectionColor="#8b5cf6"
              fadeDistance={20}
            />
          )}

          <OrbitControls makeDefault minDistance={1} maxDistance={10} />
        </Suspense>
      </Canvas>
    </div>
  );
}
