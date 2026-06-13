"""
Pydantic schemas for Digital Twin and ProductDigitalTwinSpec.
This is the comprehensive spec described in the system requirements.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# ProductDigitalTwinSpec — Sub-schemas
# ──────────────────────────────────────────────

class Vec3(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class Quaternion(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0


class PBRMaterial(BaseModel):
    name: str
    base_color: str = "#CCCCCC"
    base_color_texture: str | None = None
    metalness: float = 0.0
    metalness_texture: str | None = None
    roughness: float = 0.5
    roughness_texture: str | None = None
    normal_texture: str | None = None
    normal_scale: float = 1.0
    ao_texture: str | None = None
    emissive_color: str | None = None
    emissive_texture: str | None = None
    emissive_intensity: float = 0.0
    opacity: float = 1.0
    alpha_mode: str = "opaque"  # opaque, mask, blend


class JointSpec(BaseModel):
    """Physics joint specification for interactive parts."""
    type: str = "fixed"  # fixed, revolute, prismatic, spherical
    axis: Vec3 = Field(default_factory=lambda: Vec3(x=0, y=1, z=0))
    limits: dict[str, float] | None = None  # min, max angle/distance
    spring_stiffness: float = 0.0
    damping: float = 0.0
    snap_points: list[float] | None = None
    motor_speed: float | None = None


class ColliderSpec(BaseModel):
    type: str = "cuboid"  # cuboid, sphere, capsule, hull, trimesh
    size: Vec3 | None = None
    radius: float | None = None
    height: float | None = None
    friction: float = 0.5
    restitution: float = 0.2
    mass: float | None = None


class InteractionEvent(BaseModel):
    trigger: str  # click, release, drag, rotate, toggle
    effects: list[dict[str, Any]] = []  # animation, screen_change, sound, state_transition


class PartSpec(BaseModel):
    """Specification for a single part of the product."""
    id: str
    name: str
    parent_id: str | None = None
    position: Vec3 = Field(default_factory=Vec3)
    rotation: Quaternion = Field(default_factory=Quaternion)
    scale: Vec3 = Field(default_factory=lambda: Vec3(x=1, y=1, z=1))
    pivot: Vec3 = Field(default_factory=Vec3)

    # Geometry reference
    mesh_name: str | None = None  # Reference to mesh in GLB

    # Material
    material: PBRMaterial | None = None

    # Physics
    is_interactive: bool = False
    collider: ColliderSpec | None = None
    joint: JointSpec | None = None

    # Interactions
    events: list[InteractionEvent] = []
    hotspot_label: str | None = None
    hotspot_description: str | None = None

    # Screen content (for display parts)
    screen_content: dict[str, Any] | None = None

    # AI confidence
    confidence: float = 1.0
    confidence_source: str | None = None


class StateTransition(BaseModel):
    from_state: str
    to_state: str
    trigger: str
    guard: str | None = None
    effects: list[dict[str, Any]] = []


class StateMachineSpec(BaseModel):
    """Deterministic state machine for product behavior."""
    initial_state: str = "default"
    states: list[str] = ["default"]
    transitions: list[StateTransition] = []


class LightSpec(BaseModel):
    type: str = "point"  # point, spot, directional, ambient
    color: str = "#FFFFFF"
    intensity: float = 1.0
    position: Vec3 = Field(default_factory=Vec3)
    target: Vec3 | None = None
    angle: float | None = None  # For spot lights
    decay: float = 2.0
    cast_shadow: bool = False


class LODLevel(BaseModel):
    level: int
    distance: float
    triangle_count: int
    glb_key: str | None = None


class ProductDigitalTwinSpec(BaseModel):
    """
    The complete specification for a product digital twin.
    This is the central data structure that drives the entire system.
    """

    # Identity
    product_name: str
    brand: str | None = None
    model_number: str | None = None
    category: str = "electronics"

    # Dimensions (in meters for 3D, stored as mm in project)
    dimensions: Vec3 = Field(default_factory=Vec3)
    units: str = "meters"
    accuracy_mode: str = "commercial"  # commercial, engineering

    # Parts hierarchy
    parts: list[PartSpec] = []

    # State machine
    state_machine: StateMachineSpec = Field(default_factory=StateMachineSpec)

    # Lighting
    lights: list[LightSpec] = []
    environment_map: str | None = None

    # LOD
    lod_levels: list[LODLevel] = []

    # Display modes
    display_modes: list[str] = ["default"]  # exploded, wireframe, xray, etc.

    # Audio
    sounds: dict[str, str] = {}  # event_name -> audio_file_key

    # Performance targets
    target_fps_mobile: int = 30
    target_fps_desktop: int = 60
    max_triangles: int = 100000
    texture_resolution: int = 2048

    # AI provenance
    generation_provider: str | None = None
    ai_decisions: list[dict[str, Any]] = []
    overall_confidence: float = 0.0


# ──────────────────────────────────────────────
# API Response Schemas
# ──────────────────────────────────────────────

class DigitalTwinResponse(BaseModel):
    id: str
    project_id: str
    status: str
    version: int
    spec: dict[str, Any] | None = None
    glb_url: str | None = None
    usdz_url: str | None = None
    thumbnail_url: str | None = None
    quality_score: float | None = None
    ai_confidence: float | None = None
    is_published: bool = False
    publish_url: str | None = None
    embed_code: str | None = None
    triangle_count: int | None = None
    file_size_bytes: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DigitalTwinUpdate(BaseModel):
    spec: dict[str, Any] | None = None
    status: str | None = None


class PublishRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    allow_embed: bool = True
    custom_domain: str | None = None


class ValidateResponse(BaseModel):
    is_valid: bool
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    quality_score: float | None = None
    performance_metrics: dict[str, Any] | None = None
