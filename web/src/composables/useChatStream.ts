// frontend/src/composables/useChatStream.ts

import { ref, type Ref, unref } from "vue";
import { ttsBus } from '@/bus/ttsBus';
import type { ChatMessage, BackendStreamChunk } from "@/types/web/chat";
import { createThinkAccumulator } from "./useThinkParser";

type MaybeRef<T> = T | Ref<T>

export function useChatStream(opts: {
  messages: MaybeRef<ChatMessage[]>;
  ttsText: Ref<string>;
  ttsPlay: Ref<boolean>;
  scrollToBottom?: () => void;            // ← 改为可选
  getAuthToken: () => string | null;
  getSessionId?: () => string | null;
  getAppType?: () => string | null;
}) {
  const {
    messages,
    ttsText,
    ttsPlay,
    scrollToBottom = () => {},            // ← 默认 no-op
    getAuthToken,
    getSessionId = () => null,
    getAppType = () => null,
  } = opts;

  const sessionReady = ref(false);
  const creatingSession = ref(false);
  const streamingIndex = ref<number | null>(null);
  const progress = ref<{ completed: number; total: number }>({ completed: 0, total: 0 });

  const thinkAcc = createThinkAccumulator();

  // 统一封装带会话头
  function withSessionHeaders(h: Record<string, string>) {
    const sid = getSessionId?.() || null;
    console.log("会话 id 为：", sid);
    if (sid) h['X-Session-Id'] = sid;
    return h;
  }

  async function createSession(): Promise<void> {
    const token = getAuthToken();
    if (creatingSession.value || sessionReady.value) return;
    creatingSession.value = true;
    try {
      const resp = await fetch("/api/v1/auth/session", {
        method: "POST",
        headers: {
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: "",
      });
      if (!resp.ok) throw new Error(`创建会话失败，状态：${resp.status}`);
      sessionReady.value = true;
    } finally {
      creatingSession.value = false;
    }
  }

  async function postChatStream(messagesForApi: ChatMessage[]): Promise<Response> {
    const url = "/api/v1/chatbot/chat/stream";
    const token = getAuthToken();
    const headers: Record<string, string> = withSessionHeaders({
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    });
    const appType = getAppType() || undefined;
    const payload: any = { messages: messagesForApi };
    if (appType) {
      payload.app_type = appType;
    }

    const resp = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      credentials: 'include',
    });
    if (!resp.ok) throw new Error(`请求失败，状态：${resp.status}`);
    return resp;
  }

  let ttsCache = "";

  async function streamAnswer({
    messagesForApi,
    index,
  }: {
    messagesForApi: ChatMessage[];
    index: number;
  }): Promise<void> {
    try {
      // 为本条消息重置解析状态
      thinkAcc.reset(index);

      ttsCache = "";
      ttsText.value = "";
      ttsPlay.value = false;
      streamingIndex.value = index;

      ttsBus.emit('tts:start');

      const response = await postChatStream(messagesForApi);
      const reader = response.body?.getReader();
      let is_summary = false;
      if (!reader) return;

      const decoder = new TextDecoder("utf-8");
      let leftover = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        leftover += decoder.decode(value || new Uint8Array(), { stream: true });
        const lines = leftover.split("\n");
        leftover = lines.pop() || "";

        for (const raw of lines) {
          const line = raw.trim();
          if (!line.startsWith("data: ")) continue;

          const jsonStr = line.slice(6);
          if (!jsonStr || jsonStr === "[DONE]") continue;

          let parsed: BackendStreamChunk;
          try {
            parsed = JSON.parse(jsonStr);
          } catch {
            continue;
          }

          // 统一拿到可变的消息数组引用
          const list = unref(messages) as ChatMessage[];

          if (parsed.event === "stream_output" && typeof parsed.content === "string") {
            const msg = list[index];
            if (!msg) continue;

            const { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            if (thinkingDelta && msg.role === "assistant") {
              msg.thinking = (msg.thinking || "") + thinkingDelta;
            }
            if (visibleDelta && msg.role === "assistant") {
              msg.content += visibleDelta;
              ttsCache += visibleDelta;
              ttsText.value = ttsCache;

              ttsBus.emit('tts:delta', visibleDelta);
            }

            scrollToBottom();
          } else if (parsed.event === "summarize" && typeof parsed.content === "string") {

            ttsBus.emit('tts:stop');

            is_summary = true;

            const msg = (unref(messages) as ChatMessage[])[index];
            if (!msg) continue;

            const { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            if (thinkingDelta && msg.role === "assistant") {
              msg.thinking = (msg.thinking || "") + thinkingDelta;
            }
            if (visibleDelta && msg.role === "assistant") {
              msg.summary = (msg.summary ?? "") + visibleDelta;
              ttsCache += visibleDelta;
              ttsText.value = ttsCache;

              ttsBus.emit('tts:delta', visibleDelta);
            }

            scrollToBottom();
          } else if (parsed.event === "done") {
            console.log("流式输出已经结束，开始获取推荐回答")
    
            let messageData = {};
            const content = parsed.content;
            
            // 详细日志，帮助排查格式问题
            console.log("原始content类型:", typeof content);
            console.log("原始content值:", content);
            
            try {
                if (typeof content === 'string') {
                    // 尝试清理可能的无效字符（常见问题处理）
                    const cleanedContent = content
                        .trim()
                        .replace(/^[\u200B-\u200D\uFEFF]/, ''); // 移除可能的零宽字符
                    
                    messageData = JSON.parse(cleanedContent);
                } else if (typeof content === 'object' && content !== null) {
                    messageData = content;
                } else {
                    console.warn("content既不是字符串也不是对象，无法解析");
                }
            } catch (e) {
                console.error("解析messageData失败:", e);
                // 尝试提取可能的message_id（应急方案）
                if (typeof content === 'string') {
                    const idMatch = content.match(/"message_id"\s*:\s*"([^"]+)"/);
                    if (idMatch && idMatch[1]) {
                        console.log("通过正则提取到message_id:", idMatch[1]);
                        messageData.message_id = idMatch[1];
                    }
                }
            }
            
            // 提取进度信息（兼容后端直接返回 progress）
            const p = (messageData.assistant?.progress || messageData.progress) as {
              completed?: number;
              total?: number;
            };
            if (p && typeof p.completed === "number" && typeof p.total === "number") {
              progress.value = {
                completed: Math.max(0, p.completed),
                total: Math.max(0, p.total),
              };
            }

             // 如果不需要推荐回答，直接跳过后续逻辑
            if (is_summary) {
              continue; // 或者直接 return，视你想不想继续处理其他 done 之后的逻辑
            }
            
            // 提取消息 ID
            const messageId = messageData.message_id || "";
            console.log("最终获取到的message_id:", messageId)
            
            if (!messageId) {
                console.log("未获取到有效的message_id，请检查content格式");
                return;
            }


            try {
              const token = getAuthToken();
              console.log("开始请求推荐回答接口")
              const listSuggested = await fetchSuggestedAnswers(messageId, token || undefined);
              const msg = (unref(messages) as ChatMessage[])[index];
              if (msg && msg.role === "assistant") {
                msg.suggestions = listSuggested || [];
                scrollToBottom();
              }
            } catch (e) {
              console.error("获取推荐回答失败：", e);
            }
          }

        }
      }

      ttsBus.emit('tts:end');

      ttsPlay.value = true;
    } catch (err) {
      console.error(err);
      const list = unref(messages) as ChatMessage[];
      if (list[index]) list[index].content += "\n[对话失败，请稍后重试]";
      ttsBus.emit('tts:end');
    } finally {
      streamingIndex.value = null;
    }
  }

  async function fetchSuggestedAnswers(messageId: string, token?: string): Promise<string[]> {
    const appType = getAppType?.() || "";
    const qs = new URLSearchParams();
    if (appType) qs.set("app_type", appType);

    const url =
      `/api/v1/chatbot/message/suggested/${encodeURIComponent(messageId)}` +
      (qs.toString() ? `?${qs.toString()}` : "");

    const headers: Record<string, string> = withSessionHeaders({
      Accept: "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    });

    const resp = await fetch(url, { method: "GET", headers, credentials: "include" });
    if (!resp.ok) throw new Error(`获取推荐回答失败：${resp.status}`);
    const data = await resp.json();
    return Array.isArray(data) ? data : [];
  }

  return {
    sessionReady,
    creatingSession,
    streamingIndex,
    createSession,
    streamAnswer,
    fetchSuggestedAnswers,
    progress,
  };
}
