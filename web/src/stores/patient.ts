// frontend/src/stores/patient.ts

import { defineStore } from 'pinia'
import type { PatientBase, PatientDetail } from '@/types/web/patient'

const LS_OPENID_KEY = 'wx_openid'
const LS_LAST_SCAN_KEY = 'last_scan_code'

export const usePatientStore = defineStore('patient', {
  state: () => ({
    base: null as PatientBase | null,
    detail: null as PatientDetail | null,
    scanCode: '',
    openid: '' as string, 
    isLoading: false,
    errorMsg: null as string | null,
  }),
  actions: {           
    /** 从本地恢复 openid / scanCode（可在应用启动时调用一次） */
    restoreFromLocal() {
      try {
        const oid = localStorage.getItem(LS_OPENID_KEY) || ''
        const lastScan = localStorage.getItem(LS_LAST_SCAN_KEY) || ''
        if (oid) this.openid = oid
        if (lastScan) this.scanCode = lastScan
      } catch {
        // ignore
      }
    },

    /** 显式设置 openid，并做本地持久化 */
    async setOpenId(openid: string) {
      this.openid = (openid || '').trim()
      try {
        if (this.openid) {
          localStorage.setItem(LS_OPENID_KEY, this.openid)
        } else {
          localStorage.removeItem(LS_OPENID_KEY)
        }
      } catch {
        // ignore
      }
      // await this.fetchPatientDataWithOpenid(this.openid)
    },

    async fetchPatientData(patientId: string) {
      this.isLoading = true
      this.errorMsg = null
      try {
        const [baseRes, detailRes] = await Promise.all([
          fetch(`/api/v1/patient/base?patient_id=${encodeURIComponent(patientId)}`),
          fetch(`/api/v1/patient/detail?patient_id=${encodeURIComponent(patientId)}`),
        ])
        if (!baseRes.ok || !detailRes.ok) {
          throw new Error(`status ${baseRes.status}/${detailRes.status}`)
        }
        this.base = await baseRes.json()
        this.detail = await detailRes.json()
      } catch (err: unknown) {
        this.errorMsg = err instanceof Error ? err.message : String(err)
      } finally {
        this.isLoading = false
        console.log("patient detail:", this.detail)
      }
    },

    async fetchPatientDataWithOpenid(openid: string) {
      this.isLoading = true
      this.errorMsg = null
      try {
        const [baseRes, detailRes] = await Promise.all([
          fetch(`/api/v1/patient/base?open_id=${encodeURIComponent(openid)}`),
          fetch(`/api/v1/patient/detail?open_id=${encodeURIComponent(openid)}`),
        ])
        if (!baseRes.ok || !detailRes.ok) {
          throw new Error(`status ${baseRes.status}/${detailRes.status}`)
        }
        this.base = await baseRes.json()
        this.detail = await detailRes.json()
        console.log("patient detail:", this.detail)
      } catch (err: unknown) {
        this.errorMsg = err instanceof Error ? err.message : String(err)
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 记录“扫码”。这里将传入的 code 当作 patient_id 使用。
     * 当 openid 交换成功后，会把 openid 直接传入此方法。
     */
    async recordScan(code: string) {
      this.scanCode = code.trim()
      // 落地最近一次 scanCode
      try {
        if (this.scanCode) {
          localStorage.setItem(LS_LAST_SCAN_KEY, this.scanCode)
        } else {
          localStorage.removeItem(LS_LAST_SCAN_KEY)
        }
      } catch {
        // ignore
      }
      await this.fetchPatientData(this.scanCode)
    },
  },
})
