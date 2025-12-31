// src/api/session.ts
export interface SessionResponse {
  session_id: string;
  name: string;
  token: string;
}

export async function apiCreateSession(getAuthToken: () => string | null): Promise<SessionResponse> {
  const token = getAuthToken?.() || null;
  const resp = await fetch('/api/v1/auth/session', {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: '', // 后端无请求体
    credentials: 'include',
  });
  if (!resp.ok) throw new Error(`创建会话失败，状态：${resp.status}`);
  const data = (await resp.json()) as SessionResponse;
  if (!data?.session_id || !data?.token) throw new Error('响应缺少 session_id 或 token');
  return data;
}
