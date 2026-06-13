/**
 * Pro3duct API Client — fetch wrapper for all backend communication.
 * Handles JWT tokens, base URL, and error formatting.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
  if (typeof window !== "undefined") {
    if (token) localStorage.setItem("pro3duct_token", token);
    else localStorage.removeItem("pro3duct_token");
  }
}

export function getAuthToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== "undefined") {
    authToken = localStorage.getItem("pro3duct_token");
  }
  return authToken;
}

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {}
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

/* ─── Auth ─── */
export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  tenant_id?: string;
}

export async function register(email: string, password: string, fullName: string) {
  const data = await request<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
      tenant_name: `${fullName}'s Workspace`,
    }),
  });
  setAuthToken(data.access_token);
  return data;
}

export async function login(email: string, password: string) {
  const data = await request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(data.access_token);
  return data;
}

export async function devLogin() {
  const data = await request<AuthResponse>("/auth/dev-login", {
    method: "POST",
    body: JSON.stringify({}),
  });
  setAuthToken(data.access_token);
  return data;
}

export async function getMe() {
  return request<UserResponse>("/auth/me");
}

export function logout() {
  setAuthToken(null);
}

/* ─── Projects ─── */
export interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  category: string;
  quality_mode: string;
  privacy_policy: string;
  status: string;
  brand: string | null;
  model_number: string | null;
  width_mm: number | null;
  height_mm: number | null;
  depth_mm: number | null;
  weight_grams: number | null;
  budget_cents: number;
  asset_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  items: ProjectResponse[];
  total: number;
  page: number;
  page_size: number;
}

export async function listProjects(page = 1, search?: string) {
  const params = new URLSearchParams({ page: String(page) });
  if (search) params.set("search", search);
  return request<ProjectListResponse>(`/projects?${params}`);
}

export async function createProject(data: {
  name: string;
  description?: string;
  category?: string;
  quality_mode?: string;
  privacy_policy?: string;
  brand?: string;
  model_number?: string;
  width_mm?: number;
  height_mm?: number;
  depth_mm?: number;
  weight_grams?: number;
  budget_cents?: number;
}) {
  return request<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getProject(id: string) {
  return request<ProjectResponse>(`/projects/${id}`);
}

export async function deleteProject(id: string) {
  return request<void>(`/projects/${id}`, { method: "DELETE" });
}

/* ─── Assets ─── */
export interface AssetResponse {
  id: string;
  project_id: string;
  asset_type: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  is_validated: boolean;
  created_at: string;
}

export async function uploadAssets(projectId: string, files: File[], assetType = "image") {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  form.append("asset_type", assetType);
  return request<AssetResponse[]>(`/projects/${projectId}/assets`, {
    method: "POST",
    body: form,
  });
}

export async function listAssets(projectId: string) {
  return request<AssetResponse[]>(`/projects/${projectId}/assets`);
}

/* ─── Generation ─── */
export interface JobResponse {
  id: string;
  project_id: string;
  status: string;
  progress_percent: number;
  current_step: string | null;
  active_provider: string | null;
  total_cost_cents: number;
  created_at: string;
  updated_at: string;
}

export async function startGeneration(projectId: string) {
  return request<JobResponse>(`/projects/${projectId}/generate`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function getJobStatus(jobId: string) {
  return request<JobResponse>(`/jobs/${jobId}`);
}

export interface GenerationCapabilities {
  real_3d_enabled: boolean;
  demo_generation_enabled: boolean;
  active_provider: string | null;
  missing_config: string[];
  max_images: number;
  supported_image_types: string[];
  input_method: string;
  cost_note: string;
}

export async function getGenerationCapabilities() {
  return request<GenerationCapabilities>("/generation/capabilities");
}

/* ─── Health ─── */
export async function healthCheck() {
  return request<{ status: string }>("/health");
}

/* ─── Digital Twins ─── */
export interface DigitalTwinResponse {
  id: string;
  project_id: string;
  status: string;
  version: number;
  spec: any | null;
  glb_url: string | null;
  usdz_url: string | null;
  thumbnail_url: string | null;
  quality_score: number | null;
  ai_confidence: number | null;
  is_published: boolean;
  publish_url: string | null;
  embed_code: string | null;
  triangle_count: number | null;
  file_size_bytes: number | null;
  created_at: string;
  updated_at: string;
}

export async function getDigitalTwin(twinId: string) {
  return request<DigitalTwinResponse>(`/digital-twins/${twinId}`);
}

export async function getPublicDigitalTwin(twinId: string) {
  return request<DigitalTwinResponse>(`/digital-twins/public/${twinId}`);
}

export async function getDigitalTwinByProject(projectId: string) {
  return request<DigitalTwinResponse>(`/digital-twins/project/${projectId}`);
}

export async function updateDigitalTwin(twinId: string, spec: any, status?: string) {
  return request<DigitalTwinResponse>(`/digital-twins/${twinId}`, {
    method: "PATCH",
    body: JSON.stringify({ spec, status }),
  });
}

export interface ValidationResponse {
  is_valid: boolean;
  errors: { code: string; message: string }[];
  warnings: { code: string; message: string }[];
  quality_score: number;
}

export async function validateDigitalTwin(twinId: string) {
  return request<ValidationResponse>(`/digital-twins/${twinId}/validate`, {
    method: "POST",
  });
}

export interface PublishResponse {
  publish_url: string;
  embed_code: string;
  status: string;
}

export async function publishDigitalTwin(
  twinId: string,
  options: { title?: string; description?: string; allow_embed?: boolean } = {}
) {
  return request<PublishResponse>(`/digital-twins/${twinId}/publish`, {
    method: "POST",
    body: JSON.stringify({
      title: options.title,
      description: options.description,
      allow_embed: options.allow_embed !== false,
    }),
  });
}

/* ─── Provider Credentials (BYOK) ─── */
export interface SystemProviderResponse {
  name: string;
  display_name: string;
  provider_type: string;
  capabilities: string[];
  status: string;
  quality_tier: number;
  is_on_premise: boolean;
}

export interface ProviderCredentialResponse {
  id: string;
  provider_name: string;
  label: string;
  is_active: boolean;
  total_requests: number;
  total_cost_cents: number;
}

export async function listSystemProviders() {
  return request<SystemProviderResponse[]>("/providers/system");
}

export async function listCredentials() {
  return request<ProviderCredentialResponse[]>("/providers/credentials");
}

export async function addCredential(providerName: string, apiKey: string, label: string) {
  return request<ProviderCredentialResponse>("/providers/credentials", {
    method: "POST",
    body: JSON.stringify({ provider_name: providerName, api_key: apiKey, label }),
  });
}

export async function deleteCredential(credentialId: string) {
  return request<void>(`/providers/credentials/${credentialId}`, {
    method: "DELETE",
  });
}
