<template>
  <div class="page-container">
    
    <header class="header desktop-only">
      <div class="header-back" @click="goBackToChat">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon-back" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        <span class="back-text">返回对话</span>
      </div>

      <div class="header-title-box">
        <span class="header-title">预问诊报告</span>
      </div>
    </header>

    <div id="patient-info" class="patient-info-bar">
      <div class="patient-info-wrapper">
        
        <div class="identity-row">
          
          <div class="identity-left">
            <div class="avatar-box">
              <img v-if="genderText === '男'" src="@/assets/man.svg" alt="男" class="avatar-img" />
              <img v-else-if="genderText === '女'" src="@/assets/woman.svg" alt="女" class="avatar-img" />
              <img v-else src="@/assets/man.svg" alt="默认" class="avatar-img opacity-60" />
            </div>

            <div class="name-age-box">
              <span class="patient-name">{{ baseName || '—' }}</span>
              
              <div class="gender-icon-box">
                <img v-if="genderText === '男'" src="@/assets/男.svg" class="gender-icon" alt="m" />
                <img v-else-if="genderText === '女'" src="@/assets/女.svg" class="gender-icon" alt="f" />
              </div>

              <span v-if="baseAge !== null" class="patient-age">
                {{ baseAge }}岁
              </span>
            </div>
          </div>

          <div class="mobile-visit-id mobile-only">
             {{ visitNumber || '—' }}
          </div>

        </div>

        <div class="mobile-dates-row mobile-only">
           <div class="date-item">
             <span class="date-label">出生日期:</span>
             <span class="date-value">{{ birthdayText || '—' }}</span>
           </div>
           <div class="date-item">
             <span class="date-label">就诊日期:</span>
             <span class="date-value">{{ visitDateText || '—' }}</span>
           </div>
        </div>

        <div class="desktop-details-group desktop-only">
          <div class="detail-item">
             <span class="detail-label">门诊号:</span>
             <span class="detail-value">{{ visitNumber || '—' }}</span>
          </div>
          <div class="detail-item">
             <span class="detail-label">出生日期:</span>
             <span class="detail-value">{{ birthdayText || '—' }}</span>
          </div>
          <div class="detail-item">
             <span class="detail-label">就诊日期:</span>
             <span class="detail-value">{{ visitDateText || '—' }}</span>
          </div>
        </div>

      </div>
    </div>

    <div id="report-content" class="report-content-area">
      <div class="report-card">
        <div class="report-sections-container">
          
          <section class="report-section">
            <div class="section-header">
              <div class="blue-bar"></div>
              <span class="section-title">主诉</span>
            </div>
            <p class="section-body">
              {{ parsed.chiefComplaint || lastRecordChief || '—' }}
            </p>
          </section>

          <section class="report-section">
            <div class="section-header">
              <div class="blue-bar"></div>
              <span class="section-title">现病史</span>
            </div>
            <p class="section-body">
              {{ parsed.presentIllness || lastRecordPresent || '—' }}
            </p>
          </section>

          <section class="report-section">
            <div class="section-header">
              <div class="blue-bar"></div>
              <span class="section-title">既往史</span>
            </div>
            <p class="section-body">
              {{ parsed.pastHistory || pastHistoryText || '—' }}
            </p>
          </section>

          <section class="report-section" v-if="genderText !== '男'">
            <div class="section-header">
              <div class="blue-bar"></div>
              <span class="section-title">婚育史</span>
            </div>
            <p class="section-body">
              <span v-if="parsed.marriageFamily?.marriage">{{ parsed.marriageFamily.marriage }}</span>
              <span v-else-if="marriageText">{{ marriageText }}</span>
              <span v-else>—</span>
            </p>
          </section>

          <section class="report-section">
            <div class="section-header">
              <div class="blue-bar"></div>
              <span class="section-title">家族史</span>
            </div>
            <p class="section-body">
              <span v-if="parsed.marriageFamily?.family">{{ parsed.marriageFamily.family }}</span>
              <span v-else-if="familyText">{{ familyText }}</span>
              <span v-else>—</span>
            </p>
          </section>

          <section v-if="summaryText" class="report-section original-chat-bg">
            <div class="section-header-spread">
              <div class="header-left">
                <div class="gray-bar"></div>
                <span class="section-title gray-title">原始对话</span>
              </div>
              <button type="button" class="toggle-btn" @click="showOriginal = !showOriginal">
                {{ showOriginal ? '收起' : '展开' }}
              </button>
            </div>
            <div v-if="showOriginal" class="original-content-box">
               <p class="original-text">
                 {{ summaryText }}
               </p>
            </div>
          </section>

        </div>
      </div>
      <div class="bottom-spacer"></div>
    </div>

    <div id="back-to-chat-mobile" class="mobile-bottom-bar mobile-only-flex">
      <button class="mobile-btn" @click="goBackToChat">
        返回对话
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { usePatientStore } from '@/stores/patient'
import { useSummaryStore } from '@/stores/summary'
import { useRouter } from 'vue-router'

const patientStore = usePatientStore()
const summaryStore = useSummaryStore()
const router = useRouter()

const showOriginal = ref(true)

// --- 基础字段 ---
const baseName = computed(() => patientStore.base?.name || patientStore.detail?.patientIdentity?.patientName || '')
const baseAge = computed(() => patientStore.base?.age ?? null)
const genderText = computed(() => {
  const g = patientStore.detail?.latestMedicalRecord?.basicInfo?.gender
  if (!g) return ''
  if (g === 'M') return '男'
  if (g === 'F') return '女'
  if (g === '男' || g === '女') return g
  return String(g)
})
const birthdayText = computed(() => fmtDate(patientStore.detail?.latestMedicalRecord?.basicInfo?.birthday))
const visitNumber = computed(() => patientStore.base?.visit_number || patientStore.detail?.visitInfo?.visitNumber || '')
const visitDateText = computed(() => {
  const d = patientStore.detail?.visitInfo?.visitDate
  return fmtDate(d || new Date().toISOString())
})

// --- 逻辑处理 (核心修改部分) ---
const summaryText = computed(() => {
  const t = summaryStore.text
  return typeof t === 'string' ? t.trim() : (t ? String(t) : '')
})

function parseSummary(raw: string) {
  const out = {
    chiefComplaint: '', 
    presentIllness: '', 
    pastHistory: '',
    marriageFamily: { marriage: '', family: '' }
  }
  if (!raw) return out

  // 1. 预处理：统一格式
  // 将 "婚育史\n" 或 "婚育史 " 或 "婚育史：" 统一转换为 "婚育史："
  // 这样可以兼容 AI 输出的标题后直接换行的情况
  let text = raw
    .replace(/\r\n?/g, '\n') // 统一换行符
    // 核心正则：匹配行首或换行后的标题，后面跟着冒号或者换行，统一加冒号
    .replace(/(?:^|\n)\s*(主诉|现病史|既往史|婚育史|婚育|家族史)(?:\s*[:：]|\s*(?=\n)|$)/g, '\n$1：')
    .replace(/[ \t]+/g, ' ') // 压缩空格
    .trim()

  type Key = 'chief' | 'present' | 'past' | 'marriage' | 'family'
  
  // 2. 定位所有标题
  const allTitleRe = /(主诉|现病史|既往史|婚育史|婚育|家族史)\s*：/gi
  type Hit = { key: Key; start: number; end: number }
  const hits: Hit[] = []
  let m: RegExpExecArray | null
  
  while ((m = allTitleRe.exec(text))) {
    const label = m[1]
    let key: Key | null = null
    if (/主诉/i.test(label)) key = 'chief'
    else if (/现病史/i.test(label)) key = 'present'
    else if (/既往史/i.test(label)) key = 'past'
    else if (/婚育史|婚育/i.test(label)) key = 'marriage'
    else if (/家族史/i.test(label)) key = 'family'
    
    if (key) hits.push({ key, start: m.index, end: m.index + m[0].length })
  }

  // 如果没有匹配到任何标题，则全部作为现病史
  if (!hits.length) { 
    out.presentIllness = raw; // 此时用 raw 防止被 replace 破坏格式
    return out 
  }

  // 3. 截取内容
  hits.sort((a, b) => a.start - b.start)
  const pieces: Partial<Record<Key, string>> = {}
  
  for (let i = 0; i < hits.length; i++) {
    const { key, end } = hits[i]
    const nextStart = i + 1 < hits.length ? hits[i + 1].start : text.length
    pieces[key] = text.slice(end, nextStart).trim()
  }

  out.chiefComplaint = (pieces.chief ?? '').trim()
  out.presentIllness = (pieces.present ?? '').trim()
  out.pastHistory = (pieces.past ?? '').trim()

  // 4. 处理婚育史和家族史
  // 优先使用明确提取到的字段
  const explicitMarriage = (pieces.marriage ?? '').trim()
  const explicitFamily = (pieces.family ?? '').trim()

  // 处理婚育史
  if (explicitMarriage) {
    // 如果没有明确的家族史章节，尝试检查婚育史里是否混杂了家族史（兼容旧逻辑）
    if (!explicitFamily) {
      const lines = explicitMarriage.split(/[\n。]+/).map((s) => s.trim()).filter(Boolean)
      const mBuf: string[] = [], fBuf: string[] = []
      lines.forEach(l => /(家族|直系|遗传|父母|兄弟|姐妹|肿瘤家族史)/.test(l) ? fBuf.push(l) : mBuf.push(l))
      
      out.marriageFamily.marriage = mBuf.join('。').replace(/。+$/, '')
      // 如果拆分出了家族内容，填入 family
      if (fBuf.length > 0) {
        out.marriageFamily.family = fBuf.join('。').replace(/。+$/, '')
      }
    } else {
      // 如果已经明确有家族史章节，则直接赋值，不做拆分
      out.marriageFamily.marriage = explicitMarriage
    }
  }

  // 处理家族史 (如果明确提取到了家族史，覆盖上面的逻辑)
  if (explicitFamily) {
    out.marriageFamily.family = explicitFamily
  }

  return out
}
const parsed = computed(() => parseSummary(summaryText.value))

// --- 档案数据兜底 (保持不变) ---
const lastRecordChief = computed(() => patientStore.detail?.revisitInfo?.lastRecord?.chiefComplaint || '')
const lastRecordPresent = computed(() => patientStore.detail?.revisitInfo?.lastRecord?.presentIllness || '')
const pastHistoryText = computed(() => {
  const p = patientStore.detail?.latestMedicalRecord?.pastHistory
  if (!p) return ''
  const buf: string[] = []
  if (p.diseaseHistory) buf.push(`疾病史：${p.diseaseHistory}`)
  if (p.surgeryHistory) buf.push(`手术史：${p.surgeryHistory}`)
  if (p.bloodTransfusionHistory) buf.push(`输血史：${p.bloodTransfusionHistory}`)
  if (p.epidemiologicalHistory) buf.push(`流调史：${p.epidemiologicalHistory}`)
  if (p.personalHistory) buf.push(`个人史：${p.personalHistory}`)
  if (patientStore.detail?.latestMedicalRecord?.allergyHistory) buf.push(`过敏史：${patientStore.detail.latestMedicalRecord.allergyHistory}`)
  return buf.join('；')
})
const marriageText = computed(() => {
  const m = patientStore.detail?.latestMedicalRecord?.marriageChildInfo
  if (!m) return ''
  const parts: string[] = []
  if (m.marriageStatus) parts.push(`婚姻：${m.marriageStatus}`)
  const ob: string[] = []
  if (m.fullTermCount != null) ob.push(`足月产 ${m.fullTermCount}`)
  if (m.prematureCount != null) ob.push(`早产 ${m.prematureCount}`)
  if (m.abortionCount != null) ob.push(`流产 ${m.abortionCount}`)
  if (m.livingChildrenCount != null) ob.push(`存活 ${m.livingChildrenCount}`)
  if (ob.length) parts.push(`孕产：${ob.join('，')}`)
  return parts.join('；')
})
const familyText = computed(() => patientStore.detail?.latestMedicalRecord?.pastHistory?.familyHistory || '')

function fmtDate(input?: string) {
  if (!input) return ''
  const d = new Date(input)
  if (isNaN(d.getTime())) return input
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
import { useChatHistoryStore } from '@/stores/chatHistory'
import { useAppStore } from '@/stores/app'

const chatHistoryStore = useChatHistoryStore()
const appStore = useAppStore()

function goBackToChat() {
  const sid = chatHistoryStore.sessionId
  const platform = appStore.platform

  if (platform === "app") {
      router.push({
      path: '/chat',
      query: sid ? { sid } : undefined,
    })
  } else {
    router.back()
  }
}

</script>

<style scoped>
* { box-sizing: border-box; }
.page-container {
  width: 100%; height: 100vh; display: flex; flex-direction: column; background-color: #f5f7fa; overflow: hidden;
}

/* --- 响应式辅助类 --- */
/* 默认（手机端）状态 */
.desktop-only { display: none !important; }
.mobile-only { display: block; }
.mobile-only-flex { display: flex; }

/* -----------------------------------
   顶部 Header
----------------------------------- */
.header {
  background-color: #fff; border-bottom: 1px solid #e5e7eb; height: 50px; padding: 0 16px;
  align-items: center; flex-shrink: 0; position: relative; z-index: 20;
}
.header-back {
  position: absolute; left: 16px; top: 0; height: 100%; display: flex; align-items: center;
  cursor: pointer; color: #374151;
}
.icon-back { width: 20px; height: 20px; mr: 4px; }
.back-text { font-size: 15px; font-weight: 500; }
.header-title-box { width: 100%; display: flex; justify-content: center; }
.header-title { font-size: 16px; font-weight: 600; color: #1f2937; }

/* -----------------------------------
   患者信息栏 (高度定制)
----------------------------------- */
.patient-info-bar {
  background-color: #fff; border-bottom: 1px solid #e5e7eb; padding: 16px; flex-shrink: 0; z-index: 10;
}
.patient-info-wrapper {
  width: 100%; display: flex; flex-direction: column; gap: 12px;
}

/* 第一行：身份信息 */
.identity-row {
  display: flex; align-items: center; justify-content: space-between; width: 100%;
}
.identity-left {
  display: flex; align-items: center;
}
.avatar-box {
  width: 44px; height: 44px; border-radius: 50%; overflow: hidden; background-color: #dbeafe;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.name-age-box {
  margin-left: 12px; display: flex; align-items: center; flex-wrap: wrap;
}
.patient-name {
  font-size: 17px; font-weight: 700; color: #111827; margin-right: 6px;
}
.gender-icon-box {
  display: flex; align-items: center; margin-right: 6px;
}
.gender-icon { width: 14px; height: 14px; }
.patient-age { font-size: 14px; color: #4b5563; }

.mobile-visit-id {
  font-size: 13px; color: #9ca3af;
}

/* 第二行：日期 (手机端) */
.mobile-dates-row {
  display: flex; justify-content: space-between; margin-top: 4px; padding-top: 4px;
}
.date-item {
  font-size: 13px; color: #6b7280;
}
.date-label { color: #9ca3af; margin-right: 4px; }
.date-value { color: #4b5563; }

/* 桌面端详细信息 (默认隐藏) */
.desktop-details-group {
  display: none; flex-direction: row; gap: 32px; font-size: 14px; color: #6b7280;
}
.detail-item { display: flex; align-items: center; }
.detail-label { margin-right: 8px; color: #9ca3af; }
.detail-value { color: #1f2937; font-weight: 500; }

/* -----------------------------------
   报告内容
----------------------------------- */
.report-content-area {
  flex: 1; overflow-y: auto; padding: 12px; scroll-behavior: smooth;
  scrollbar-width: thin; scrollbar-color: #e5e7eb transparent;
}
.report-content-area::-webkit-scrollbar { width: 6px; }
.report-content-area::-webkit-scrollbar-track { background: transparent; }
.report-content-area::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 3px; }

.report-card {
  width: 100%; background-color: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  overflow: hidden; min-height: calc(100vh - 180px);
}
.report-section { padding: 16px; border-bottom: 1px solid #f3f4f6; }
.report-section:last-child { border-bottom: none; }

.section-header { display: flex; align-items: center; margin-bottom: 12px; }
.section-header-spread { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.header-left { display: flex; align-items: center; }
.blue-bar { width: 4px; height: 16px; background-color: #246bff; border-radius: 2px; margin-right: 8px; }
.gray-bar { width: 4px; height: 16px; background-color: #9ca3af; border-radius: 2px; margin-right: 8px; }
.section-title { font-size: 15px; font-weight: 700; color: #1f2937; }
.gray-title { color: #4b5563; }
.section-body {
  font-size: 14px; color: #374151; line-height: 1.75; white-space: pre-line; padding-left: 12px; margin: 0;
}
.original-chat-bg { background-color: rgba(249, 250, 251, 0.8); }
.toggle-btn { font-size: 14px; color: #246bff; background: none; border: none; cursor: pointer; }
.original-content-box { padding-left: 12px; margin-top: 8px; }
.original-text { font-size: 13px; color: #6b7280; white-space: pre-line; line-height: 1.6; margin: 0; }
.bottom-spacer { height: 40px; }

/* 底部按钮 (手机端) */
.mobile-bottom-bar {
  background-color: #fff; border-top: 1px solid #e5e7eb; padding: 12px 16px;
  justify-content: center; flex-shrink: 0;
}
.mobile-btn {
  width: 100%; height: 44px; border-radius: 6px; background-color: #246bff;
  color: white; font-size: 15px; font-weight: 500; border: none; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* =================================================================
   Desktop / Tablet Styles (min-width: 768px)
================================================================= */
@media (min-width: 768px) {
  
  /* 显示桌面端元素 */
  .desktop-only { display: flex !important; }
  
  /* 隐藏移动端元素 */
  .mobile-only { display: none !important; }
  .mobile-only-flex { display: none !important; }

  /* 调整患者信息布局为横向 */
  .patient-info-wrapper {
    flex-direction: row; align-items: center; justify-content: flex-start;
    padding: 0 24px; gap: 48px;
  }
  
  .identity-row { width: auto; margin-right: auto; }
  .avatar-box { width: 48px; height: 48px; }
  
  .report-content-area { padding: 24px; }
  .report-card { box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
  .report-section { padding: 24px 32px; }
  .section-title { font-size: 16px; }
  .section-body { font-size: 15px; }
}
</style>