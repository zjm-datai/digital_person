// frontend/src/composables/useChatStream.ts
import { ref, type Ref, unref } from "vue";
import { ttsBus } from "@/bus/ttsBus";
import type { ChatMessage } from "@/types/web/chat";
import { createThinkAccumulator } from "./useThinkParser";

import { apiCompletionMessages, apiGetSuggestedAnswers } from "@/api/chat";

type MaybeRef<T> = T | Ref<T>;

/**
 * 适配你们后端 SSE 的 chunk 结构：
 * - ask_stream: 增量文本（主回答）
 * - ask_end: 完整文本（主回答兜底）
 * - summarize_stream: 增量文本（总结）
 * - summarize_end: 完整文本（总结兜底，可选）
 * - message_context: 携带 conversation_id / progress / message_id（可能分多条发）
 * - is_end: bool
 */
type ConsoleStreamChunk =
  | { event: "ask_stream"; content: string }
  | { event: "ask_end"; content: string }
  | { event: "summarize_stream"; content: string }
  | { event: "summarize_end"; content: string }
  | { event: "message_context"; content: any }
  | { event: "is_end"; content: boolean }
  | { event: string; content: any };

export function useChatStream(opts: {
  messages: MaybeRef<ChatMessage[]>;
  ttsText: Ref<string>;
  ttsPlay: Ref<boolean>;
  scrollToBottom?: () => void;

  // 新接口必须
  getAppType?: () => string | null; // URL path param
  getOpcId?: () => string | null; // body.opc_id
  getConversationId?: () => string | null; // body.conversation_id（可选）

  // 可选：后端会在 message_context 里返回 conversation_id
  setConversationId?: (cid: string) => void;

  /**
   * 可选：是否拉取推荐回答
   * - 默认：当本次流里出现 summarize_stream / summarize_end 时，不拉推荐
   */
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

  // 进度：后端 message_context 里可能给，也可能 null
  const progress = ref<{ completed: number; total: number }>({ completed: 0, total: 0 });

  const thinkAcc = createThinkAccumulator();

  /**
   * 新接口只需要单条 message：从 messagesForApi 里找最后一条 user
   */
  function getLastUserMessage(messagesForApi: ChatMessage[]) {
    for (let i = messagesForApi.length - 1; i >= 0; i--) {
      const m = messagesForApi[i];
      if (m?.role === "user") return (m.content || "").trim();
    }
    return "";
  }

  /**
   * 调用新 SSE 接口：POST /apps/<app_type>/completion-messages
   */
  async function postCompletionStream(messagesForApi: ChatMessage[]): Promise<Response> {
    const appType = (getAppType?.() || "").trim();
    if (!appType) throw new Error("缺少 appType（getAppType 返回空）");

    const opcId = (getOpcId?.() || "").trim();
    if (!opcId) throw new Error("缺少 opc_id（getOpcId 返回空）");

    const conversationId = (getConversationId?.() || "").trim() || undefined;
    const message = getLastUserMessage(messagesForApi);
    if (!message) throw new Error("缺少用户 message（messagesForApi 中未找到 user 消息）");

    return await apiCompletionMessages(appType, {
      opc_id: opcId,
      conversation_id: conversationId,
      message,
      response_mode: "streaming",
    });
  }

  let ttsCache = "";

  async function streamAnswer({
    messagesForApi,
    index,
  }: {
    messagesForApi: ChatMessage[];
    index: number;
  }): Promise<void> {
    let hasSummaryStream = false;
    let hasAskStream = false;

    try {
      // 为本条消息重置解析状态
      thinkAcc.reset(index);

      ttsCache = "";
      ttsText.value = "";
      ttsPlay.value = false;
      streamingIndex.value = index;

      // 默认开启 TTS（主回答阶段使用）
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
          const msg = list[index];
          if (!msg) continue;

          // ================
          // 1) ask_stream：主回答增量输出
          // ================
          if (parsed.event === "ask_stream" && typeof parsed.content === "string") {
            hasAskStream = true;

            let { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            // 去掉 </think> 后多余的 \n\n
            if (visibleDelta) {
              const prev = msg.content || "";

              // 如果刚好以 </think> 结尾，而当前是纯换行 → 丢弃
              if (prev.endsWith("</think>") && /^\s*$/.test(visibleDelta)) {
                visibleDelta = "";
              }

              // 如果本段包含 </think>\n\n 这种，也顺手清掉
              visibleDelta = visibleDelta.replace(/<\/think>\s*\n+/g, "</think>");
            }

            if (thinkingDelta && msg.role === "assistant") {
              msg.thinking = (msg.thinking || "") + thinkingDelta;
            }

            if (visibleDelta && msg.role === "assistant") {
              msg.content = (msg.content || "") + visibleDelta;

              // 主回答才走 TTS
              ttsCache += visibleDelta;
              ttsText.value = ttsCache;
              ttsBus.emit("tts:delta", visibleDelta);
            }

            scrollToBottom();
            continue;
          }

          // ================
          // 2) summarize_stream：总结增量输出（写入 msg.summary）
          //    且：总结阶段默认不拉推荐回答（由 shouldFetchSuggestions 控制）
          // ================
          if (parsed.event === "summarize_stream" && typeof parsed.content === "string") {
            hasSummaryStream = true;
let { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            // 去掉 </think> 后多余的 \n\n
            if (visibleDelta) {
              const prev = msg.content || "";

              // 如果刚好以 </think> 结尾，而当前是纯换行 → 丢弃
              if (prev.endsWith("</think>") && /^\s*$/.test(visibleDelta)) {
                visibleDelta = "";
              }

              // 如果本段包含 </think>\n\n 这种，也顺手清掉
              visibleDelta = visibleDelta.replace(/<\/think>\s*\n+/g, "</think>");
            }

            if (thinkingDelta && msg.role === "assistant") {
              msg.summary = (msg.summary || "") + thinkingDelta;
            }

            if (visibleDelta && msg.role === "assistant") {
              msg.summary = (msg.summary || "") + visibleDelta;

              // 主回答才走 TTS
              ttsCache += visibleDelta;
              ttsText.value = ttsCache;
              ttsBus.emit("tts:delta", visibleDelta);
            }

            scrollToBottom();
            continue;
          }

          // ================
          // 3) ask_end：主回答完整输出（兜底校准）
          // ================
          if (parsed.event === "ask_end" && typeof parsed.content === "string") {
            let { visibleDelta, thinkingDelta } = thinkAcc.ingest(index, parsed.content);

            if (thinkingDelta && msg.role === "assistant") {
              msg.thinking = (msg.thinking || "") + thinkingDelta;
            }

            if (msg.role === "assistant") {
              const finalText = (visibleDelta || parsed.content) as string;

              // 若 finalText 更长，覆盖以保证最终一致；否则保留已有内容
              const currentText = msg.content || "";
              if (finalText.length >= currentText.length) {
                msg.content = finalText;
              } else if (!currentText) {
                msg.content = finalText;
              }

              // 同步 TTS 缓存（仍然只针对主回答）
              ttsCache = msg.content || "";
              ttsText.value = ttsCache;
            }

            scrollToBottom();
            continue;
          }

          // ================
          // 4) summarize_end：总结完整输出（兜底校准，可选）
          // ================
          if (parsed.event === "summarize_end" && typeof parsed.content === "string") {
            hasSummaryStream = true;

            if (msg.role === "assistant") {
              const finalSummary = parsed.content;
              const currentSummary = msg.summary || "";
              if (finalSummary.length >= currentSummary.length) {
                msg.summary = finalSummary;
              } else if (!currentSummary) {
                msg.summary = finalSummary;
              }
            }

            scrollToBottom();
            continue;
          }

          // ================
          // 5) message_context：拿 message_id / conversation_id / progress
          // ================
          if (parsed.event === "message_context" && parsed.content) {
            const c = parsed.content;

            // message_id（后续用于推荐回答）
            const mid = c?.message_id;
            if (typeof mid === "string" && mid) {
              (msg as any)._messageId = mid;
            }

            // conversation_id（后端真实会话 id）
            const cid = c?.assistant?.conversation_id;
            if (typeof cid === "string" && cid) {
              setConversationId(cid);
            }

            // progress（可能为 null）
            const p = c?.assistant?.progress;
            if (p && typeof p.completed === "number" && typeof p.total === "number") {
              progress.value = {
                completed: Math.max(0, p.completed),
                total: Math.max(0, p.total),
              };
            }

            continue;
          }

          // ================
          // 6) is_end：流程是否结束
          // ================
          if (parsed.event === "is_end") {
            // 未来若 true，可在这里做 “完成问诊” 的 UI 处理
            continue;
          }

          // 其他事件：忽略
        }
      }

      // =========================
      // 流结束后：拉推荐回答（可按总结阶段关闭）
      // =========================
      try {
        const list = unref(messages) as ChatMessage[];
        const msg = list[index];
        if (!msg || msg.role !== "assistant") return;

        // ✅ 总结阶段默认不拉推荐（也可以通过 shouldFetchSuggestions 覆盖）
        if (!shouldFetchSuggestions({ hasSummaryStream, hasAskStream, msg })) return;

        const messageId = (msg as any)?._messageId as string | undefined;
        if (messageId) {
          const appType = (getAppType?.() || "").trim();
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
      const list = unref(messages) as ChatMessage[];
      if (list[index]) list[index].content = (list[index].content || "") + "\n[对话失败，请稍后重试]";
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
