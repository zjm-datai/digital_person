// frontend/src/stores/patient.ts
import { defineStore } from "pinia";
import type { PatientBase, PatientDetail } from "@/types/web/patient";

import { apiGetPatientBase, apiGetPatientDetail } from "@/api/patient";

const LS_OPENID_KEY = "wx_openid";
const LS_LAST_SCAN_KEY = "last_scan_code";

export const usePatientStore = defineStore("patient", {
  state: () => ({
    base: null as PatientBase | null,
    detail: null as PatientDetail | null,
    scanCode: "",
    openid: "" as string,
    isLoading: false,
    errorMsg: null as string | null,
  }),

  actions: {
    restoreFromLocal() {
      try {
        const oid = localStorage.getItem(LS_OPENID_KEY) || "";
        const lastScan = localStorage.getItem(LS_LAST_SCAN_KEY) || "";
        if (oid) this.openid = oid;
        if (lastScan) this.scanCode = lastScan;
      } catch {}
    },

    async setOpenId(openid: string) {
      this.openid = (openid || "").trim();
      try {
        if (this.openid) localStorage.setItem(LS_OPENID_KEY, this.openid);
        else localStorage.removeItem(LS_OPENID_KEY);
      } catch {}
    },

    /**
     * 根据 opc_id 拉取 base + detail
     * 后端是 POST JSON: { opc_id }
     */
    async fetchPatientData(opcId: string): Promise<PatientDetail | null> {
      this.isLoading = true;
      this.errorMsg = null;

      try {
        const [base, detail] = await Promise.all([
          apiGetPatientBase(opcId),
          apiGetPatientDetail(opcId),
        ]);

        this.base = base;
        this.detail = detail;
        return this.detail;
      } catch (err: unknown) {
        this.errorMsg = err instanceof Error ? err.message : String(err);
        return null;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 记录扫码（code 就是 opc_id）
     */
    async recordScan(code: string): Promise<PatientDetail | null> {
      this.scanCode = (code || "").trim();

      try {
        if (this.scanCode) localStorage.setItem(LS_LAST_SCAN_KEY, this.scanCode);
        else localStorage.removeItem(LS_LAST_SCAN_KEY);
      } catch {}

      if (!this.scanCode) return null;
      return await this.fetchPatientData(this.scanCode);
    },

    /**
     * 你现在的后端 patient_base/detail 都是 opc_id 入参
     * 如果后面你们新增了 openid -> opc_id 的接口，再在 api 层加方法，然后这里调用即可。
     */
    async fetchPatientDataWithOpenid(_openid: string): Promise<PatientDetail | null> {
      this.errorMsg = "当前后端 patient_base/detail 接口仅支持 opc_id（JSON: { opc_id }），openid 版本接口未实现";
      return null;
    },
  },
});
