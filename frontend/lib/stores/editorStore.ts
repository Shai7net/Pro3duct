import { create } from "zustand";

export interface PartSpec {
  id: string;
  name: string;
  type: "enclosure" | "display" | "button" | "switch" | "door" | "drawer" | "other";
  visible: boolean;
  material: {
    color: string;
    roughness: number;
    metalness: number;
    opacity: number;
  };
  interaction?: {
    type: string;
    axis?: [number, number, number];
    limit_mm?: number;
    snap?: boolean;
  };
}

export interface LightSpec {
  id: string;
  type: "ambient" | "directional" | "point" | "spot";
  color: string;
  intensity: number;
  position: [number, number, number];
}

export interface TwinSpec {
  product_name: string;
  parts: PartSpec[];
  lights: LightSpec[];
  state_machine: {
    initial_state: string;
    states: string[];
    transitions: {
      from_state: string;
      to_state: string;
      trigger_event: string;
    }[];
  };
}

interface EditorState {
  // Spec state
  spec: TwinSpec | null;
  setSpec: (spec: TwinSpec) => void;

  // Selected Part/Light state
  selectedPartId: string | null;
  selectedLightId: string | null;
  selectPart: (partId: string | null) => void;
  selectLight: (lightId: string | null) => void;

  // Editor modes
  activeTab: "hierarchy" | "materials" | "interactions" | "lighting" | "states";
  setActiveTab: (tab: "hierarchy" | "materials" | "interactions" | "lighting" | "states") => void;

  // Operations
  updatePartMaterial: (partId: string, material: Partial<PartSpec["material"]>) => void;
  updatePartInteraction: (partId: string, interaction: Partial<PartSpec["interaction"]> | null) => void;
  addLight: (light: LightSpec) => void;
  updateLight: (lightId: string, updates: Partial<LightSpec>) => void;
  deleteLight: (lightId: string) => void;
  updateStateMachine: (updates: Partial<TwinSpec["state_machine"]>) => void;
}

export const useEditorStore = create<EditorState>((set) => ({
  spec: null,
  selectedPartId: null,
  selectedLightId: null,
  activeTab: "hierarchy",

  setSpec: (spec) => set({ spec }),

  selectPart: (partId) => set({ selectedPartId: partId, selectedLightId: null }),
  selectLight: (lightId) => set({ selectedLightId: lightId, selectedPartId: null }),

  setActiveTab: (tab) => set({ activeTab: tab }),

  updatePartMaterial: (partId, materialUpdates) =>
    set((state) => {
      if (!state.spec) return {};
      const updatedParts = state.spec.parts.map((part) => {
        if (part.id === partId) {
          return {
            ...part,
            material: {
              ...part.material,
              ...materialUpdates,
            },
          };
        }
        return part;
      });
      return {
        spec: {
          ...state.spec,
          parts: updatedParts,
        },
      };
    }),

  updatePartInteraction: (partId, interactionUpdates) =>
    set((state) => {
      if (!state.spec) return {};
      const updatedParts = state.spec.parts.map((part) => {
        if (part.id === partId) {
          return {
            ...part,
            interaction: interactionUpdates
              ? {
                  type: "press",
                  ...part.interaction,
                  ...interactionUpdates,
                }
              : undefined,
          };
        }
        return part;
      });
      return {
        spec: {
          ...state.spec,
          parts: updatedParts,
        },
      };
    }),

  addLight: (light) =>
    set((state) => {
      if (!state.spec) return {};
      return {
        spec: {
          ...state.spec,
          lights: [...(state.spec.lights || []), light],
        },
      };
    }),

  updateLight: (lightId, updates) =>
    set((state) => {
      if (!state.spec) return {};
      const updatedLights = (state.spec.lights || []).map((light) => {
        if (light.id === lightId) {
          return { ...light, ...updates };
        }
        return light;
      });
      return {
        spec: {
          ...state.spec,
          lights: updatedLights,
        },
      };
    }),

  deleteLight: (lightId) =>
    set((state) => {
      if (!state.spec) return {};
      return {
        spec: {
          ...state.spec,
          lights: (state.spec.lights || []).filter((light) => light.id !== lightId),
        },
      };
    }),

  updateStateMachine: (updates) =>
    set((state) => {
      if (!state.spec) return {};
      return {
        spec: {
          ...state.spec,
          state_machine: {
            ...state.spec.state_machine,
            ...updates,
          },
        },
      };
    }),
}));
