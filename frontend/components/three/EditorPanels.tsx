"use client";

import React, { useState } from "react";
import { Sliders, Sun, Shield, Layers, HelpCircle, Power, Play, Key, Trash, Plus } from "lucide-react";
import { useEditorStore, LightSpec } from "@/lib/stores/editorStore";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { heLabel } from "@/lib/hebrew";

// ─── Hierarchy / Part Selector Panel ───
export function HierarchyPanel() {
  const spec = useEditorStore((state) => state.spec);
  const selectedPartId = useEditorStore((state) => state.selectedPartId);
  const selectPart = useEditorStore((state) => state.selectPart);

  if (!spec) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-primary)" }}>חלקי המודל</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {spec.parts.map((part) => {
          const isSelected = part.id === selectedPartId;
          return (
            <div
              key={part.id}
              onClick={() => selectPart(part.id)}
              className="glass-panel"
              style={{
                padding: "10px 14px",
                cursor: "pointer",
                borderLeft: isSelected ? "4px solid var(--primary)" : "1px solid var(--glass-border)",
                background: isSelected ? "rgba(139, 92, 246, 0.1)" : "rgba(255, 255, 255, 0.02)",
                transition: "all var(--transition-fast)",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <span style={{ fontWeight: 600, fontSize: "0.85rem", color: "var(--text-primary)" }}>
                  {part.name}
                </span>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginLeft: "8px" }}>
                  ({heLabel(part.type)})
                </span>
              </div>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {part.visible ? "מוצג" : "מוסתר"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Material Editor Panel ───
export function MaterialPanel() {
  const spec = useEditorStore((state) => state.spec);
  const selectedPartId = useEditorStore((state) => state.selectedPartId);
  const updatePartMaterial = useEditorStore((state) => state.updatePartMaterial);

  if (!spec || !selectedPartId) {
    return (
      <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "24px" }}>
        בחר חלק במודל או ברשימת החלקים כדי לערוך את החומר שלו.
      </div>
    );
  }

  const selectedPart = spec.parts.find((p) => p.id === selectedPartId);
  if (!selectedPart) return null;

  const mat = selectedPart.material || { color: "#cccccc", roughness: 0.5, metalness: 0.0, opacity: 1.0 };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)" }}>
        עריכת חומר: {selectedPart.name}
      </h3>

      {/* Color picker */}
      <div>
        <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
          צבע בסיס
        </label>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <input
            type="color"
            value={mat.color}
            onChange={(e) => updatePartMaterial(selectedPartId, { color: e.target.value })}
            style={{
              width: "48px",
              height: "36px",
              border: "1px solid var(--glass-border)",
              borderRadius: "4px",
              background: "transparent",
              cursor: "pointer",
            }}
          />
          <input
            type="text"
            value={mat.color}
            onChange={(e) => updatePartMaterial(selectedPartId, { color: e.target.value })}
            style={{
              flex: 1,
              background: "rgba(255,255,255,0.03)",
              border: "1px solid var(--glass-border)",
              borderRadius: "var(--border-radius)",
              padding: "8px 12px",
              color: "#fff",
              fontSize: "0.85rem",
            }}
          />
        </div>
      </div>

      {/* Roughness */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontSize: "0.8rem" }}>
          <span style={{ color: "var(--text-secondary)" }}>חספוס</span>
          <span style={{ color: "var(--text-primary)" }}>{mat.roughness}</span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={mat.roughness}
          onChange={(e) => updatePartMaterial(selectedPartId, { roughness: parseFloat(e.target.value) })}
          style={{ width: "100%", accentColor: "var(--primary)" }}
        />
      </div>

      {/* Metalness */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontSize: "0.8rem" }}>
          <span style={{ color: "var(--text-secondary)" }}>מתכתיות</span>
          <span style={{ color: "var(--text-primary)" }}>{mat.metalness}</span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={mat.metalness}
          onChange={(e) => updatePartMaterial(selectedPartId, { metalness: parseFloat(e.target.value) })}
          style={{ width: "100%", accentColor: "var(--primary)" }}
        />
      </div>

      {/* Opacity */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontSize: "0.8rem" }}>
          <span style={{ color: "var(--text-secondary)" }}>שקיפות</span>
          <span style={{ color: "var(--text-primary)" }}>{mat.opacity}</span>
        </div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={mat.opacity}
          onChange={(e) => updatePartMaterial(selectedPartId, { opacity: parseFloat(e.target.value) })}
          style={{ width: "100%", accentColor: "var(--primary)" }}
        />
      </div>
    </div>
  );
}

// ─── Interactions Editor Panel ───
export function InteractionsPanel() {
  const spec = useEditorStore((state) => state.spec);
  const selectedPartId = useEditorStore((state) => state.selectedPartId);
  const updatePartInteraction = useEditorStore((state) => state.updatePartInteraction);

  if (!spec || !selectedPartId) {
    return (
      <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "24px" }}>
        בחר חלק במודל כדי להגדיר כיצד הוא מגיב ללחיצה.
      </div>
    );
  }

  const selectedPart = spec.parts.find((p) => p.id === selectedPartId);
  if (!selectedPart) return null;

  const handleInteractionToggle = (type: string) => {
    if (type === "none") {
      updatePartInteraction(selectedPartId, null);
    } else {
      updatePartInteraction(selectedPartId, { type });
    }
  };

  const hasInteraction = !!selectedPart.interaction;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)" }}>
        הגדרת אינטראקציה לחלק
      </h3>
      <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
        בחר האם החלק הוא קבוע, כפתור, מתג או דלת.
      </p>

      <div>
        <Select
          label="סוג האינטראקציה"
          value={selectedPart.interaction?.type || "none"}
          onChange={(e) => handleInteractionToggle(e.target.value)}
          options={[
            { value: "none", label: "חלק קבוע" },
            { value: "press", label: "כפתור לחיץ" },
            { value: "switch", label: "מתג" },
            { value: "door", label: "דלת נפתחת" },
          ]}
        />
      </div>

      {hasInteraction && (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "8px" }}>
          <div style={{ display: "flex", gap: "12px" }}>
            <Input
              label="טווח תנועה במ״מ"
              type="number"
              value={selectedPart.interaction?.limit_mm || 5}
              onChange={(e) =>
                updatePartInteraction(selectedPartId, { limit_mm: parseFloat(e.target.value) })
              }
            />
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <label style={{ fontSize: "0.875rem", fontWeight: 500, color: "var(--text-secondary)" }}>
                חזרה למקום
              </label>
              <button
                type="button"
                onClick={() =>
                  updatePartInteraction(selectedPartId, { snap: !selectedPart.interaction?.snap })
                }
                style={{
                  background: selectedPart.interaction?.snap ? "var(--primary)" : "rgba(255,255,255,0.05)",
                  color: "#fff",
                  border: "1px solid var(--glass-border)",
                  borderRadius: "var(--border-radius)",
                  padding: "10px 14px",
                  cursor: "pointer",
                  fontSize: "0.85rem",
                  fontWeight: 600,
                }}
              >
                {selectedPart.interaction?.snap ? "פעיל" : "לא פעיל"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Lighting Panel ───
export function LightingPanel() {
  const spec = useEditorStore((state) => state.spec);
  const addLight = useEditorStore((state) => state.addLight);
  const updateLight = useEditorStore((state) => state.updateLight);
  const deleteLight = useEditorStore((state) => state.deleteLight);

  if (!spec) return null;

  const handleAddNewLight = () => {
    const id = `light-${Math.random().toString(36).substring(2, 9)}`;
    const newLight: LightSpec = {
      id,
      type: "point",
      color: "#ffffff",
      intensity: 1.0,
      position: [0, 2, 1],
    };
    addLight(newLight);
  };

  const lights = spec.lights || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)" }}>הגדרת תאורה</h3>
        <Button variant="secondary" size="sm" onClick={handleAddNewLight}>
          <Plus size={14} /> הוספת תאורה
        </Button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {lights.length === 0 ? (
          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", textAlign: "center" }}>
            לא נוספו מקורות תאורה. מוצגת תאורת ברירת המחדל.
          </p>
        ) : (
          lights.map((light) => (
            <div
              key={light.id}
              className="glass-panel"
              style={{
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                gap: "12px",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 700, fontSize: "0.85rem", color: "var(--text-primary)", textTransform: "capitalize" }}>
                  תאורה {heLabel(light.type)}
                </span>
                <button
                  onClick={() => deleteLight(light.id)}
                  style={{ background: "transparent", border: "none", color: "var(--danger)", cursor: "pointer" }}
                >
                  <Trash size={14} />
                </button>
              </div>

              <div>
                <label style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>עוצמה</label>
                <input
                  type="range"
                  min="0"
                  max="3"
                  step="0.1"
                  value={light.intensity}
                  onChange={(e) => updateLight(light.id, { intensity: parseFloat(e.target.value) })}
                  style={{ width: "100%", accentColor: "var(--primary)" }}
                />
              </div>

              <div style={{ display: "flex", gap: "10px" }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>צבע</label>
                  <input
                    type="color"
                    value={light.color}
                    onChange={(e) => updateLight(light.id, { color: e.target.value })}
                    style={{ width: "100%", height: "28px", border: "none", cursor: "pointer", background: "transparent" }}
                  />
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ─── State Machine Panel ───
export function StatesPanel() {
  const spec = useEditorStore((state) => state.spec);
  const updateStateMachine = useEditorStore((state) => state.updateStateMachine);

  if (!spec || !spec.state_machine) return null;

  const [fromState, setFromState] = useState("");
  const [toState, setToState] = useState("");
  const [trigger, setTrigger] = useState("");

  const handleAddTransition = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fromState || !toState || !trigger) return;

    const existingTrans = spec.state_machine.transitions || [];
    const newTrans = {
      from_state: fromState,
      to_state: toState,
      trigger_event: trigger,
    };

    updateStateMachine({
      transitions: [...existingTrans, newTrans],
    });

    setFromState("");
    setToState("");
    setTrigger("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "var(--text-primary)" }}>מצבי פעולה</h3>
      <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
        הגדר כיצד לחיצה על חלק משנה את מצב המוצר.
      </p>

      {/* States List */}
      <div className="glass-panel" style={{ padding: "14px" }}>
        <h4 style={{ fontSize: "0.85rem", color: "var(--text-primary)", marginBottom: "8px" }}>מצבים מוגדרים</h4>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {spec.state_machine.states.map((st) => (
            <Badge key={st} variant={st === spec.state_machine.initial_state ? "success" : "info"}>
              {st}
            </Badge>
          ))}
        </div>
      </div>

      {/* Transitions List */}
      <div className="glass-panel" style={{ padding: "14px" }}>
        <h4 style={{ fontSize: "0.85rem", color: "var(--text-primary)", marginBottom: "8px" }}>מעברים בין מצבים</h4>
        {spec.state_machine.transitions.length === 0 ? (
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>עדיין לא הוגדרו מעברים.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {spec.state_machine.transitions.map((t, idx) => (
              <div key={idx} style={{ fontSize: "0.75rem", color: "var(--text-secondary)", display: "flex", gap: "8px", alignItems: "center" }}>
                <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{t.from_state}</span>
                <span>➔</span>
                <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{t.to_state}</span>
                <span style={{ color: "var(--text-muted)" }}>({t.trigger_event})</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Transition form */}
      <form onSubmit={handleAddTransition} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        <h4 style={{ fontSize: "0.85rem", color: "var(--text-primary)" }}>הוספת מעבר</h4>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
          <Input
            placeholder="ממצב, לדוגמה off"
            value={fromState}
            onChange={(e) => setFromState(e.target.value)}
          />
          <Input
            placeholder="למצב, לדוגמה on"
            value={toState}
            onChange={(e) => setToState(e.target.value)}
          />
        </div>
        <Input
          placeholder="אירוע מפעיל, לדוגמה press_power_button"
          value={trigger}
          onChange={(e) => setTrigger(e.target.value)}
        />
        <Button type="submit" variant="secondary" size="sm">
          הוספת המעבר
        </Button>
      </form>
    </div>
  );
}
