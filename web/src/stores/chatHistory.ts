// src/stores/chatHistory.ts
import { defineStore } from "pinia";
import type { ChatMessage } from "@/types/web/chat";
import { trimEnds } from "@/utils/textNormalize";

function sanitize(m: ChatMessage): ChatMessage {
  const anyMsg: any = m as any;
  return {
    ...m,
    content: trimEnds(anyMsg.content || ""),
    summary: trimEnds(anyMsg.summary || ""),
    thinking: trimEnds(anyMsg.thinking || ""),
  } as any;
}

export const useChatHistoryStore = defineStore("chatHistory", {
  state: () => ({
    sessionId: null as string | null,
    messages: [] as ChatMessage[],
  }),
  actions: {
    resetForSession(sid: string | null) {
      if (sid && this.sessionId === sid) return;
      this.sessionId = sid;
      this.messages = [];
    },

    reset() {
      this.sessionId = null;
      this.messages = [];
    },

    set(messages: ChatMessage[]) {
      this.messages = (messages || []).map(sanitize);
    },

    push(msg: ChatMessage) {
      this.messages.push(sanitize(msg));
    },
  },
});
