"use client";

import React, { useMemo, useState } from "react";
import { Center, useGLTF } from "@react-three/drei";
import { useEditorStore, PartSpec } from "@/lib/stores/editorStore";

interface ProductViewerProps {
  glbUrl?: string | null;
}

function GeneratedGlbModel({
  glbUrl,
  onClick,
}: {
  glbUrl: string;
  onClick: (e: any) => void;
}) {
  const { scene } = useGLTF(glbUrl);
  const clonedScene = useMemo(() => scene.clone(true), [scene]);

  return (
    <Center>
      <group onClick={onClick}>
        <primitive object={clonedScene} />
      </group>
    </Center>
  );
}

export default function ProductViewer({ glbUrl }: ProductViewerProps) {
  const spec = useEditorStore((state) => state.spec);
  const selectedPartId = useEditorStore((state) => state.selectedPartId);
  const selectPart = useEditorStore((state) => state.selectPart);

  // Maintain local animated state for clicked buttons/doors
  const [buttonPressed, setButtonPressed] = useState(false);
  const [doorOpen, setDoorOpen] = useState(false);
  const [switchToggled, setSwitchToggled] = useState(false);

  if (!spec || !spec.parts) return null;

  const handleModelClick = (e: any) => {
    e.stopPropagation();
    selectPart(spec.parts[0]?.id || null);
  };

  const dynamicLights = spec.lights?.map((light) => {
    if (light.type === "point") {
      return (
        <pointLight
          key={light.id}
          color={light.color}
          intensity={light.intensity}
          position={light.position}
        />
      );
    }
    if (light.type === "directional") {
      return (
        <directionalLight
          key={light.id}
          color={light.color}
          intensity={light.intensity}
          position={light.position}
          castShadow
        />
      );
    }
    return null;
  });

  if (glbUrl) {
    return (
      <group>
        <GeneratedGlbModel glbUrl={glbUrl} onClick={handleModelClick} />
        {dynamicLights}
      </group>
    );
  }

  const handlePartClick = (part: PartSpec, e: any) => {
    e.stopPropagation();
    selectPart(part.id);

    // Dynamic animation triggers based on type
    if (part.type === "button") {
      setButtonPressed(true);
      setTimeout(() => setButtonPressed(false), 200);

      // Trigger state machine logic if present
      if (spec.state_machine) {
        const eventName = `press_${part.name}`;
        console.log(`State Machine Event Triggered: ${eventName}`);
      }
    } else if (part.type === "door") {
      setDoorOpen((prev) => !prev);
    } else if (part.type === "switch") {
      setSwitchToggled((prev) => !prev);
    }
  };

  return (
    <group>
      {spec.parts.map((part) => {
        const isSelected = part.id === selectedPartId;

        // Position offset calculations for active animations
        let yOffset = 0;
        let rotationY = 0;

        if (part.type === "button" && buttonPressed) {
          yOffset = -0.05; // Depressed effect
        }
        if (part.type === "door" && doorOpen) {
          rotationY = Math.PI / 2.5; // swing open
        }
        if (part.type === "switch" && switchToggled) {
          rotationY = Math.PI / 6; // toggle tilt
        }

        // Render mock primitives for dashboard modeling editor
        return (
          <mesh
            key={part.id}
            position={[
              part.id === "part-button" ? 0 : -0.2,
              part.id === "part-button" ? 0.35 + yOffset : 0,
              part.id === "part-button" ? 0.4 : 0,
            ]}
            rotation={[0, rotationY, 0]}
            onClick={(e) => handlePartClick(part, e)}
          >
            {part.type === "button" ? (
              <cylinderGeometry args={[0.08, 0.08, 0.08, 32]} />
            ) : (
              <boxGeometry args={[0.6, 0.5, 0.8]} />
            )}

            <meshStandardMaterial
              color={part.material?.color || "#888888"}
              roughness={part.material?.roughness ?? 0.5}
              metalness={part.material?.metalness ?? 0.0}
              transparent={part.material?.opacity !== 1.0}
              opacity={part.material?.opacity ?? 1.0}
              emissive={isSelected ? "#8b5cf6" : "#000000"}
              emissiveIntensity={isSelected ? 0.4 : 0.0}
            />
          </mesh>
        );
      })}

      {/* Render Dynamic lights from spec */}
      {dynamicLights}
    </group>
  );
}
