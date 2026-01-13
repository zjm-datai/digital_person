import { defineStore } from "pinia";
import { apiLogin, apiProfile, apiLogout } from "@/api/auth";

type User = any;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    loaded: false,
    loading: false,
    error: "" as string | null,
  }),
  getters: {
    isAuthed: (s) => !!s.user,
  },
  actions: {
    async bootstrap() {
      if (this.loaded) return;
      this.loaded = true;

      try {
        const profile = await apiProfile();
        this.user = profile;
      } catch {
        this.user = null;
      }
    },

    async login(email: string, password: string, remember_me = false) {
      this.loading = true;
      this.error = null;
      try {
        await apiLogin({ email, password, remember_me });
        // 登录成功 cookie 已写入，马上拉 me（如果你还没 /me，可注释并直接 user = {}）
        try {
          const profile = await apiProfile();
          this.user = profile;
        } catch {
          // fallback：没有 /me 时也能继续
          this.user = { email };
        }
      } catch (e: any) {
        this.user = null;
        this.error = e?.message || "登录失败";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await apiLogout();
      } catch {}
      this.user = null;
      this.loaded = true;
    },
  },
});
