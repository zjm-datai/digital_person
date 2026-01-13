
import { getCookie } from "@/utils/cookie";

const CSRF_COOKIE = "csrf_token";
const CSRF_HEADER = "X-CSRF-Token";

const REFRESH_URL = "/console_api/refresh-token";

let refreshing = false;
let waiters: Array<(ok: boolean) => void> = [];

function flush(ok: boolean) {
    waiters.forEach((w) => w(ok));
    waiters = [];
}

async function refreshToken(): Promise<boolean> {
    try {
        const resp = await fetch(REFRESH_URL, {
            method: "POST",
            credentials: "include",
            headers: { Accept: "application/json" },
        });
        return resp.ok;
    } catch {
        return false;
    }
}

function attachCsrf(headers: Headers, method: string) {
    const m = method.toUpperCase();
    // 一般只对非 GET 要求 CSRF，若后端对 GET 也校验，把判断删掉
    if (m !== "GET") {
        const csrf = getCookie(CSRF_COOKIE);
        if (csrf) headers.set(CSRF_HEADER, csrf);
    }
}

export async function fetchWithRefresh(
    input: RequestInfo | URL, 
    init: RequestInit = {}
): Promise<Response> {
    
    const method = (init.method || "GET").toUpperCase();
    const headers = new Headers(init.headers || {});

    attachCsrf(headers, method);

    const reqInit: RequestInit = {
        ...init,
        method,
        headers,
        credentials: "include", // 永远带 cookie
    };

    const resp = await fetch(input, reqInit);

    if (resp.status !== 401) return resp;

    // 防止 refresh 死循环
    const url = typeof input === "string" ? input : (input as URL).toString();
    if (url.includes("/refresh-token")) return resp;

    // 401 -> 无感刷新（带并发锁）
    if (!refreshing) {
        refreshing = true;
        const ok = await refreshToken();
        refreshing = false;
        flush(ok);

        if (!ok) return resp; // 刷新失败：交由上层处理（跳登录等）
        return fetch(input, reqInit);  // 刷新成功：重放请求
    }

    // 刷新进行中：排队等待结果
    const ok = await new Promise<boolean>((resolve) => waiters.push(resolve));
    if (!ok) return resp;
    return fetch(input, reqInit);
}