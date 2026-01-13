import { fetchWithRefresh } from "./httpClient";

export type LoginPayload = {
    email: string;
    password: string;
    remember_me?: boolean;
    invite_token?: string | null;
};

const LOGIN_URL = "/console_api/login";
const PROFILE_URL = "/console_api/account/profile"
const LOGOUT_URL = "/console_api/logout"

export async function apiLogin(payload: LoginPayload) {
    const resp = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json", 
            Accept: "application/json" 
        },
        credentials: "include",
        body: JSON.stringify(payload),
    })

    if (!resp.ok) {
        let msg = `登录失败：${resp.status}`;
        
        try {
            const data = await resp.json();
            msg = data?.message || msg;
        } catch {}
        
        throw new Error(msg);
    }
    
    return resp.json();

}

export async function apiProfile(): Promise<any> {
    const resp = await fetchWithRefresh(PROFILE_URL, { method: "GET", headers: { Accept: "application/json" } });
    if (!resp.ok) throw new Error(`profile 失败：${resp.status}`);
    return resp.json();
}

export async function apiLogout(): Promise<void> {
    const resp = await fetchWithRefresh(LOGOUT_URL, { method: "POST", headers: { Accept: "application/json" } });
    if (!resp.ok) throw new Error(`logout 失败：${resp.status}`);
}