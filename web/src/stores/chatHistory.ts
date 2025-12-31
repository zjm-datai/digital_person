// src/stores/chatHistory.ts
import { defineStore } from 'pinia'
import type { ChatMessage } from '@/types/web/chat'

export const useChatHistoryStore = defineStore('chatHistory', {
  state: () => ({
    sessionId: null as string | null,
    messages: [] as ChatMessage[],
  }),
  actions: {
    /** 切换到某个会话。如果会话变了，就把消息清空 */
    resetForSession(sid: string | null) {
      // 同一个会话，不需要清空
      if (sid && this.sessionId === sid) return

      this.sessionId = sid
      this.messages = []
    },

    /** 彻底重置（可选，用不到可以删） */
    reset() {
      this.sessionId = null
      this.messages = []
    },

    set(messages: ChatMessage[]) {
      this.messages = messages
    },

    push(msg: ChatMessage) {
      this.messages.push(msg)
    },
  },
})
