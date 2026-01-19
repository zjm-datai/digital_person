import { fetchWithRefresh } from "./httpClient";
import { ElMessage } from "element-plus";

export type Conversation = {
    id: string;
    opc_id: string;
    app_type: string;
    created_at: string;
};

function assertOk(resp: Response, data?: any) {
    if (resp.ok) return;
    // flask-restx 常见错误格式可能是 { message: "..."} 或 {msg:"..."}
    const msg =
        data?.message ||
        data?.msg ||
        data?.error ||
        `请求失败（HTTP ${resp.status}）`;
    throw new Error(msg);
}

export async function apiCreateConversation(params: {
    appType: string;
    opcId: string;
}): Promise<Conversation> {
    const { appType, opcId } = params;

    const resp = await fetchWithRefresh(
        `/console_api/apps/${encodeURIComponent(appType)}/conversation`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify({ opc_id: opcId }),
        }
    );

    let data: any = null;
    try {
        data = await resp.json();
    } catch {
        // 不是 JSON 也没关系
    }

    try {
        assertOk(resp, data);
    } catch (e: any) {
        // 静默也行，这里给个默认提示
        ElMessage.error(e?.message || "创建会话失败");
        throw e;
    }

    // flask-restx marshal_with 会把对象字段直接返回
    return data as Conversation;
}