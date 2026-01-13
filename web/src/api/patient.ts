// frontend/src/api/patient.ts
import { fetchWithRefresh } from "@/api/httpClient";
import type { PatientBase, PatientDetail } from "@/types/web/patient";

type Json = Record<string, any>;

async function readJsonSafe(resp: Response) {
  try {
    return await resp.json();
  } catch {
    return null;
  }
}

function pickErrorMessage(resp: Response, data: any) {
  return data?.message || data?.msg || data?.error || `请求失败（HTTP ${resp.status}）`;
}

/**
 * 统一的 JSON POST
 */
async function postJson<T>(url: string, body: Json): Promise<T> {
  const resp = await fetchWithRefresh(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await readJsonSafe(resp);
  if (!resp.ok) throw new Error(pickErrorMessage(resp, data));
  return data as T;
}

/**
 * 获取患者 base（后端：POST /patient_base, body: { opc_id }）
 */
export function apiGetPatientBase(opcId: string): Promise<PatientBase> {
  return postJson<PatientBase>("/console_api/patient_base", { opc_id: opcId });
}

/**
 * 获取患者 detail（后端：POST /patient_detail, body: { opc_id }）
 */
export function apiGetPatientDetail(opcId: string): Promise<PatientDetail> {
  return postJson<PatientDetail>("/console_api/patient_detail", { opc_id: opcId });
}

/**
 * 获取患者列表（后端：GET /patient_all）
 */
export async function apiGetAllPatients<T = any[]>(): Promise<T> {
  const resp = await fetchWithRefresh("/console_api/patient_all", {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  const data = await readJsonSafe(resp);
  if (!resp.ok) throw new Error(pickErrorMessage(resp, data));
  return data as T;
}
