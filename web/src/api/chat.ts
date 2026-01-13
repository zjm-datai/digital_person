
import { fetchWithRefresh } from "@/api/httpClient";

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

export type CompletionMessageReq = {
  opc_id: string;
  message: string;
  conversation_id?: string;
  response_mode?: "blocking" | "streaming";
};

/**
 * 预问诊对话（流式/非流式都走同一个接口）
 * POST /apps/<app_type>/completion-messages
 *
 * 注意：流式时 response.headers Accept: text/event-stream
 */
export async function apiCompletionMessages(
  appType: string,
  payload: CompletionMessageReq
): Promise<Response> {
  const url = `/console_api/apps/${encodeURIComponent(appType)}/completion-messages`;

  const resp = await fetchWithRefresh(url, {
    method: "POST",
    headers: {
      Accept: payload.response_mode === "blocking" ? "application/json" : "text/event-stream",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const data = await readJsonSafe(resp);
    throw new Error(pickErrorMessage(resp, data));
  }
  return resp;
}

/**
 * 推荐回答
 * GET /apps/<app_type>/chat-messages/<uuid>/suggested-answers
 * 返回：{ data: string[] }
 */
export async function apiGetSuggestedAnswers(appType: string, messageId: string): Promise<string[]> {
  const url = `/console_api/apps/${encodeURIComponent(appType)}/chat-messages/${encodeURIComponent(
    messageId
  )}/suggested-answers`;

  const resp = await fetchWithRefresh(url, {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  const data = await readJsonSafe(resp);
  if (!resp.ok) throw new Error(pickErrorMessage(resp, data));

  const list = data?.data;
  return Array.isArray(list) ? list : [];
}

/**
 * 拉取会话消息列表（你后端目前先写死 ["sssss"]）
 * POST /apps/<app_type>/chat-messages  body: { conversation_id }
 */
export async function apiListChatMessages(appType: string, conversationId: string): Promise<any> {
  const url = `/console_api/apps/${encodeURIComponent(appType)}/chat-messages`;

  const resp = await fetchWithRefresh(url, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId }),
  });

  const data = await readJsonSafe(resp);
  if (!resp.ok) throw new Error(pickErrorMessage(resp, data));
  return data;
}

import type { ChatMessage } from "@/types/web/chat";

export type ChatMessageApiRaw = {
  id: string;
  role: "assistant" | "user";
  content?: string | null;
  thinking?: string | null;
  summary?: string | null;
  suggestions?: string[] | null;
};

const HISTORY_URL = "/console_api/apps/chat-messages";

function normalizeChatMessage(m: ChatMessageApiRaw): ChatMessage {
  return {
    id: String(m.id ?? ""),
    role: m.role,
    content: typeof m.content === "string" ? m.content : "",
    thinking: typeof m.thinking === "string" ? m.thinking : "",
    summary: typeof m.summary === "string" ? m.summary : "",
    suggestions: Array.isArray(m.suggestions) ? m.suggestions : [],
  };
}

/**
 * 拉取对话历史（包含 summary-only 行）
 */
export async function getChatMessages(params: {
  conversationId: string;
  appType?: string;
}): Promise<ChatMessage[]> {
  const { conversationId, appType } = params;

  const url = new URL(HISTORY_URL, window.location.origin);
  url.searchParams.set("conversation_id", conversationId);
  if (appType) url.searchParams.set("app_type", appType);

  const resp = await fetchWithRefresh(url.toString(), {
    method: "GET",
    headers: { Accept: "application/json" },
  });

  if (!resp.ok) {
    // 让调用方决定怎么提示
    const text = await resp.text().catch(() => "");
    throw new Error(`getChatMessages failed: HTTP ${resp.status} ${text}`);
  }

  const data = (await resp.json()) as ChatMessageApiRaw[];
  if (!Array.isArray(data)) return [];

  return data.map(normalizeChatMessage);
}
