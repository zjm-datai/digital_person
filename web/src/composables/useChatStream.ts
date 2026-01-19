// frontend/src/composables/useChatStream.ts


import { ref, type Ref, unref } from "vue";
import { ttsBus } from "@/bus/ttsBus";
import type { ChatMessage } from "@/types/web/chat";
import { createThinkAccumulator } from "./useThinkParser";
import { appendAndTrim, trimEnds } from "@/utils/textNormalize";

import { apiCompletionMessages, apiGetSuggestedAnswers } from "@/api/chat";

type MaybeRef<T> = T | Ref<T>;

type ConsoleStreamChunk =
  | { event: "ask_stream"; content: string }
  | { event: "ask_end"; content: string }
  | { event: "summarize_stream"; content: string }
  | { event: "summarize_end"; content: string }
  | { event: "message_context"; content: any }
  | { event: "is_end"; content: boolean }
  | { event: string; content: any };

type TargetField = "content" | "summary";

export function useChatStream(opts: {
  messages: MaybeRef<ChatMessage[]>;
  ttsText: Ref<string>;
  ttsPlay: Ref<boolean>;
  scrollToBottom?: () => void;

  getAppType?: () => string | null;
  getOpcId?: () => string | null;
  getConversationId?: () => string | null;

  setConversationId?: (cid: string) => void;

  shouldFetchSuggestions?: (ctx: {
    hasSummaryStream: boolean;
    hasAskStream: boolean;
    msg: ChatMessage;
  }) => boolean;
}) {
  const {
    messages,
    ttsText,
    ttsPlay,
    scrollToBottom = () => {},
    getAppType = () => null,
    getOpcId = () => null,
    getConversationId = () => null,
    setConversationId = () => {},
    shouldFetchSuggestions = ({ hasSummaryStream }) => !hasSummaryStream,
  } = opts;

  const streamingIndex = ref<number | null>(null);

  const progress = ref<{ completed: number; total: number }>({ completed: 0, total: 0 });

  // 解析 think 标签（增量、支持切片、吞 </think> 后换行）
  const thinkAcc = createThinkAccumulator({ swallowAfterClose: 2 });

  function getLastUserMessage(messagesForApi: ChatMessage[]) {
    for (let i = messagesForApi.length - 1; i >= 0; i--) {
      const m = messagesForApi[i];
      if (m?.role === "user") return trimEnds((m.content || "").toString());
    }
    return "";
  }

  async function postCompletionStream(messagesForApi: ChatMessage[]): Promise<Response> {
    const appType = trimEnds(getAppType?.() || "");
    if (!appType) throw new Error("缺少 appType（getAppType 返回空）");

    const opcId = trimEnds(getOpcId?.() || "");
    if (!opcId) throw new Error("缺少 opc_id（getOpcId 返回空）");

    const conversationId = trimEnds(getConversationId?.() || "") || undefined;

    const message = getLastUserMessage(messagesForApi);
    if (!message) throw new Error("缺少用户 message（messagesForApi 中未找到 user 消息）");

    return await apiCompletionMessages(appType, {
      opc_id: opcId,
      conversation_id: conversationId,
      message,
      response_mode: "streaming",
    });
  }

  function applyThinking(msg: any, delta: string) {
    if (!delta) return;
    msg.thinking = appendAndTrim(msg.thinking || "", delta);
  }

  function applyToField(msg: any, field: TargetField, delta: string) {
    if (!delta) return;
    msg[field] = appendAndTrim(msg[field] || "", delta);
  }

  function hardTrimAll(msg: any) {
    if (!msg) return;
    msg.content = trimEnds(msg.content || "");
    msg.summary = trimEnds(msg.summary || "");
    msg.thinking = trimEnds(msg.thinking || "");
  }

  function ttsAppend(visibleDelta: string, ttsCacheRef: { value: string }) {
    if (!visibleDelta) return;
    ttsCacheRef.value += visibleDelta;
    ttsText.value = ttsCacheRef.value;
    ttsBus.emit("tts:delta", visibleDelta);
  }

  async function streamAnswer({
    messagesForApi,
    index,
  }: {
    messagesForApi: ChatMessage[];
    index: number;
  }): Promise<void> {
    let hasSummaryStream = false;
    let hasAskStream = false;

    const ttsCacheRef = { value: "" };

    try {
      thinkAcc.reset(index);

      ttsCacheRef.value = "";
      ttsText.value = "";
      ttsPlay.value = false;
      streamingIndex.value = index;

      // 默认开启 TTS（只在主回答阶段实际输出 delta）
      ttsBus.emit("tts:start");

      const response = await postCompletionStream(messagesForApi);
      const reader = response.body?.getReader();
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

          let parsed: ConsoleStreamChunk;
          try {
            parsed = JSON.parse(jsonStr);
          } catch {
            continue;
          }

          const list = unref(messages) as ChatMessage[];
          const msg: any = list[index];
          if (!msg || msg.role !== "assistant") continue;

          // message_context：message_id / conversation_id / progress
          if (parsed.event === "message_context" && parsed.content) {
            const c = parsed.content;

            const mid = c?.message_id;
            if (typeof mid === "string" && mid) msg._messageId = mid;

            const cid = c?.assistant?.conversation_id;
            if (typeof cid === "string" && cid) setConversationId(cid);

            const p = c?.assistant?.progress;
            if (p && typeof p.completed === "number" && typeof p.total === "number") {
              progress.value = {
                completed: Math.max(0, p.completed),
                total: Math.max(0, p.total),
              };
            }
            continue;
          }

          // ask_stream / summarize_stream：同一套处理逻辑
          if (
            (parsed.event === "ask_stream" || parsed.event === "summarize_stream") &&
            typeof parsed.content === "string"
          ) {
            const isAsk = parsed.event === "ask_stream";
            hasAskStream ||= isAsk;
            hasSummaryStream ||= !isAsk;

            const { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            applyThinking(msg, thinkingDelta);
            applyToField(msg, isAsk ? "content" : "summary", visibleDelta);

            // ✅ 只有主回答走 TTS
            if (isAsk) ttsAppend(visibleDelta, ttsCacheRef);

            scrollToBottom();
            continue;
          }

          // ask_end：完整输出兜底（只校准 content）
          if (parsed.event === "ask_end" && typeof parsed.content === "string") {
            const { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            applyThinking(msg, thinkingDelta);

            // 兜底：如果流式 content 为空，就用 visibleDelta 补；然后强制 trim
            if (!msg.content) applyToField(msg, "content", visibleDelta || "");
            msg.content = trimEnds(msg.content || "");

            // 同步 TTS 缓存（只对主回答）
            ttsCacheRef.value = msg.content || "";
            ttsText.value = ttsCacheRef.value;

            scrollToBottom();
            continue;
          }

          // summarize_end：完整输出兜底（校准 summary）
          if (parsed.event === "summarize_end" && typeof parsed.content === "string") {
            const { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            applyThinking(msg, thinkingDelta);

            if (!msg.summary) applyToField(msg, "summary", visibleDelta || "");
            msg.summary = trimEnds(msg.summary || "");

            scrollToBottom();
            continue;
          }

          // is_end：预留
          if (parsed.event === "is_end") continue;

          // 其他事件忽略
        }
      }

      // 流结束：确保落盘/展示一致：全部 trim
      {
        const list = unref(messages) as any[];
        const msg = list[index];
        if (msg?.role === "assistant") hardTrimAll(msg);
      }

      // 流结束后：拉推荐回答
      try {
        const list = unref(messages) as ChatMessage[];
        const msg: any = list[index];
        if (!msg || msg.role !== "assistant") return;

        if (!shouldFetchSuggestions({ hasSummaryStream, hasAskStream, msg })) return;

        const messageId = msg?._messageId as string | undefined;
        if (messageId) {
          const appType = trimEnds(getAppType?.() || "");
          if (appType) {
            const suggested = await apiGetSuggestedAnswers(appType, messageId);
            msg.suggestions = suggested || [];
            scrollToBottom();
          }
        }
      } catch (e) {
        console.error("获取推荐回答失败：", e);
      }

      ttsBus.emit("tts:end");
      ttsPlay.value = true;
    } catch (err) {
      console.error(err);
      const list = unref(messages) as any[];
      if (list[index]) {
        list[index].content = trimEnds((list[index].content || "") + "\n[对话失败，请稍后重试]");
      }
      ttsBus.emit("tts:end");
    } finally {
      streamingIndex.value = null;
    }
  }

  return {
    streamingIndex,
    streamAnswer,
    progress,
  };
}
