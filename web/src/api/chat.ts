export interface ChatMessage {
    role: "user" | "assistant" | "system";
    content: string;
}

/**
 * 与聊天接口建立流式连接
 * @param messages  发送给后端的上下文数组
 * @param onDelta   每收到一段增量时的回调
 * @param signal    可选，用于取消请求
 */
export async function streamChat(
    messages: ChatMessage[],
    onDelta: (delta: string) => void,
    signal?: AbortSignal
) {
    try {
        const res = await fetch(
            // "http://127.0.0.1:8080/api/v1/chatbot/chat/stream",
            "/api/v1/chatbot/chat/stream",
            {
                method: "POST",
                headers: {
                    accept: "application/json",
                    "Content-Type": "application/json",
                    Authorization:
                    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzYxOTAwOTEyLCJpYXQiOjE3NTkxMzYxMTIsImp0aSI6IjEtMTc1OTEzNjExMi43NDYwODUifQ.JIC9sZD3zEmqEPhicDszaAzZcBTA6vPtBpBqMm1kEDo",
                },
                body: JSON.stringify({ messages }),
                signal,
            },
        );

        if (!res.ok || !res.body) {
            throw new Error(`聊天接口请求失败，状态码: ${res.status}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split(/\r?\n/);
            buffer = lines.pop() ?? "";

            for (const line of lines) {
                if (!line.startsWith("data:")) continue;
                const payload = line.replace(/^data:\s*/, "").trim();
                if (!payload) continue;

                try {
                    const json = JSON.parse(payload);
                    if (json.done) return;
                    if (json.content) onDelta(json.content);
                } catch (_) {
                    /* 忽略解析失败的行 */
                }
            }
        }

    } catch (err) {
        if (!signal?.aborted) {
            console.error('[streamChat] 发生错误:', err);
        }
        throw err;
    }
}
    