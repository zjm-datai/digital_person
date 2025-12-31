// frontend/src/types/chat.ts
export interface ChatMessage {
    id?: string;
    role: "user" | "assistant";
    /** 普通可见文本（HTML 字符串） */
    content: string;
    /** <think>…</think> 的内容，纯文本 */
    thinking?: string;
    summary?: string;
    // 推荐回复
    suggestions?: string[];
}

// export interface BackendStreamChunk {
//     event: "stream_output" | "is_end" | "done" | "error" | "summarize";
//     content?: string;
//     done?: boolean;
// }

export type BackendStreamChunk =
  | { event: "stream_output"; content: string }                   // token 增量
  | { event: "summarize"; content: string }                       // 总结增量
  | { event: "is_end"; content: boolean }                         // 是否已完成本轮（后端就是 boolean）
  | { event: "done"; content: string }                            // assistant_message_id
  | { event: "error"; content?: { error_code?: string; message?: string } }
  // 把上下文（包含进度）带过来
  | {
      event: "message_context";
      content: {
        assistant?: {
          message_kind?: string;
          target_stage?: string | null;
          target_field?: string | null;
          progress?: { completed: number; total: number } | null; // ← 进度在这里
        };
        user?: Record<string, any>;
      };
    };