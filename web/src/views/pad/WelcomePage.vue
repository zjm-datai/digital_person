<!-- /frontend/src/view/pad/WelcomePage.vue -->

<template>
  <div class="home-root">
    <div class="hero-layer">
      <div class="hero-inner">
        <div class="hero-card">
          <div class="hero-card-pad">
            <div class="hero-text-wrap">
              <p
                class="hero-text"
                style='font-family:"SourceHanSansSCVF-Bold","Source Han Sans CN","Source Han Sans","Noto Sans SC",system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;'
              >
                为了让医生更全面了解病情、提供精准诊疗，AI会向你询问几个相关问题，麻烦您花几分钟如实回复，感谢您的配合～
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <img class="bg-img" src="/bg.png" alt="bg" draggable="false" />

    <img class="logo" src="/logo@2x.png" alt="logo" draggable="false" />

    <img
      class="doctor-illust"
      src="/医生@2x.png"
      alt="doctor"
      draggable="false"
    />
  </div>

  <div class="test-panel">
    <span class="test-label">TEST</span>
    <el-button
      class="patient-list-btn"
      size="small"
      @click="goToPatientList"
    >
      病人列表
    </el-button>
    <el-input
      ref="testInput"
      v-model="inputCode"
      placeholder="输入 code"
      size="small"
      @keyup.enter.native="handleInput(inputCode)"
      style="width: 180px"
    />
    <el-button type="primary" size="small" @click="handleInput(inputCode)"
      >确认</el-button
    >
  </div>
</template>

<script setup lang="ts">
declare global {
  interface Window {
    receiveScanFromApp?: (scanData: { data: string; timestamp: number }) => void;
  }
}

import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { ElNotification, ElMessage } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';

import { usePatientStore } from '@/stores/patient';
import { useAppStore } from '@/stores/app'; // 需包含 'phone' | 'app' | 'web'

import onScan from 'onscan.js';

const router = useRouter();
const route = useRoute();
const patientStore = usePatientStore();
const appStore = useAppStore();

const scanCode = ref('');
const scanInput = ref<HTMLInputElement | null>(null);
const inputCode = ref('');
const testInput = ref<HTMLInputElement | null>(null);

// ========= 换取 openid 相关 =========
const isExchanging = ref(false);
const hasTriedExchange = ref(false);

function getQueryFromHash(): Record<string, string | string[]> {
  const hash = window.location.hash || '';
  const qIndex = hash.indexOf('?');
  if (qIndex === -1) return {};
  const queryStr = hash.slice(qIndex + 1);
  const sp = new URLSearchParams(queryStr);
  const obj: Record<string, string | string[]> = {};
  sp.forEach((v, k) => {
    if (obj[k]) {
      obj[k] = Array.isArray(obj[k]) ? [...(obj[k] as string[]), v] : [obj[k] as string, v];
    } else {
      obj[k] = v;
    }
  });
  return obj;
}

function getAllQuery() {
  const fromRoute = route.query as Record<string, any>;
  const parsedHash = getQueryFromHash();
  const searchParams = new URLSearchParams(window.location.search || '');
  const parsedSearch: Record<string, string> = {};
  searchParams.forEach((v, k) => (parsedSearch[k] = v));
  return { ...parsedHash, ...parsedSearch, ...fromRoute } as Record<string, any>;
}

function goToPatientList() {
  router.push({ path: '/patients', query: { from: 'welcome' } });
}

function redirectByState(state: string | undefined) {
  const s = decodeURIComponent(state || '').trim();
  if (!s) return;
  if (s.startsWith('/')) {
    const [path, q] = s.split('?', 2);
    const query: Record<string, string> = {};
    if (q) new URLSearchParams(q).forEach((v, k) => (query[k] = v));
    if (appStore.platform !== 'web') query.platform = appStore.platform;
    router.replace({ path, query }).catch(() => {});
    return;
  }
  if (/^https?:\/\//i.test(s)) {
    window.location.replace(s);
    return;
  }
  router.replace({ path: `/${s}` }).catch(() => {});
}

async function exchangeCodeForOpenId(code: string) {
  const url = `/api/v1/auth/wechat/oauth2/exchange?code=${encodeURIComponent(code)}`;

  isExchanging.value = true;
  try {
    const resp = await fetch(url, { method: 'GET', credentials: 'include' });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    const openid: string | undefined = data?.openid;
    if (!openid) throw new Error('后端未返回 openid');

    patientStore.setOpenId(openid);
    
    const opcId = "PID1234563";
    await patientStore.recordScan(opcId);
    await createConversationAndGoChat(opcId);

    ElNotification({
      title: '授权成功',
      message: `已获取 openid：${openid}`,
      type: 'success',
      position: 'top-right',
      duration: 1800
    });

    return openid;
  } catch (err: any) {
    console.error('换取 openid 失败：', err);
    ElMessage.error(`换取 openid 失败：${err?.message || '未知错误'}`);
    throw err;
  } finally {
    isExchanging.value = false;
  }
}

// ========= 换取 openid 相关 =========
function syncPlatformFromUrl() {
  const fromRoute = route.query as Record<string, any>;
  const parsed = Object.keys(fromRoute || {}).length > 0 ? fromRoute : getQueryFromHash();
  const p = String(parsed.platform || '').toLowerCase();
  appStore.setPlatform(p);
}

import { apiCreateConversation } from '@/api/conversation';

function normalizeAppTypeFromDepartment(dept: string) {
  const d = (dept || "").trim();
  const map: Record<string, string> = { 
    "呼吸科": "huxike",
    "皮肤医美中心": "pifuke",
    "肛肠科": "gangchangke" 
  
  };
  return map[d] || "huxike";
}

async function createConversationAndGoChat(opcId: string, extraQuery: Record<string, any> = {}) {
  try {
    const dept = patientStore.detail?.visitInfo?.department || "";
    const appType = normalizeAppTypeFromDepartment(dept);
    const conversation = await apiCreateConversation({ appType, opcId });
    
    const q = { ...extraQuery, sid: conversation.id };
    if (appStore.platform !== 'web') {
        // @ts-ignore
        q.platform = appStore.platform;
    }
    router.push({ path: '/chat', query: q });
  } catch (e) {
    console.error('创建会话失败：', e);
  }
}

function handleScan(code: string) {
  const trimmed = (code || '').trim();
  if (!trimmed) return;

  patientStore.recordScan(trimmed).then((detail) => {
    if (!detail) {
      console.error("拉取病人详情失败")
      return;
    }
    setTimeout(() => createConversationAndGoChat(trimmed), 300);
  });

  scanCode.value = '';
}


function handleInput(code: string) {
  const trimmed = (code || '').trim();
  if (!trimmed) return;
  
  patientStore.recordScan(trimmed).then((detail) => {
    if (!detail) {
      console.error("拉取病人详情失败")
      return;
    }
    setTimeout(() => createConversationAndGoChat(trimmed), 300);
  });
}

onMounted(async () => {
  nextTick(() => scanInput.value?.focus());
  syncPlatformFromUrl();

  try {
    const fromRoute = route.query as Record<string, any>;
    const parsed = Object.keys(fromRoute || {}).length > 0 ? fromRoute : getQueryFromHash();
    const rawHash = window.location.hash || '';
    const rawSearch = window.location.search || '';
    if (Object.keys(parsed).length > 0 || rawHash || rawSearch) {
      const lines: string[] = [];
      for (const [k, v] of Object.entries(parsed)) lines.push(`${k}: ${Array.isArray(v) ? v.join(', ') : (v ?? '')}`);
    }
  } catch (e) {
    console.error('解析 URL 查询参数失败：', e);
  }

  try {
    if (!hasTriedExchange.value) {
      hasTriedExchange.value = true;

      const allQuery = getAllQuery();
      const code = String(allQuery.code || '').trim();
      if (code) {
        await exchangeCodeForOpenId(code);
      }
    }
  } catch (e) {
    // 忽略
  }

  window.addEventListener('receiveScan', (e) => {
    const event = e as CustomEvent;
    if (event.detail && typeof window.receiveScanFromApp === 'function') {
      window.receiveScanFromApp(event.detail);
    }
  });

  window.receiveScanFromApp = function (scanData: { data: string; timestamp: number }) {
    const code = scanData?.data?.trim?.() || '';
    if (code) {
      ElNotification({ message: `扫码内容：${code}`, type: 'success', position: 'top-right', duration: 2000, showClose: true });
      scanCode.value = code;
      handleScan(code);
    }
  };

  onScan.attachTo(document, {
    suffixKeyCodes: [13, 9],
    reactToPaste: true,
    minLength: 3,
    onScan: (code: string) => {
      scanCode.value = code;
      handleScan(code);
    }
  });
});

watch(() => route.fullPath, () => syncPlatformFromUrl());

onBeforeUnmount(() => {
  onScan.detachFrom(document);
});

defineExpose({
  exchangeCodeForOpenId,
  redirectByState
});
</script>

<style scoped>
/* —— 根容器 —— */
.home-root {
  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* —— 上层内容层（文字卡片所在） —— */
.hero-layer {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  min-height: 100vh;
}

/* 两侧外边距 */
.hero-inner {
  margin-left: 3vw;
  margin-right: 3vw;
  width: auto;
}

/* 卡片容器：固定尺寸与圆角（全部用 vw/vh） */
.hero-card {
  position: relative;
  display: flex;
  align-items: center;
  border: 0.15vw solid rgba(255, 255, 255, 0.8);
  border-radius: 1.2vw;
  backdrop-filter: blur(2px);
  padding: 2vw;
  box-shadow: 0 1vh 4vh -1vh rgba(0, 0, 0, 0.25);
  background: linear-gradient(124deg, rgba(250, 250, 255, 0.25) 0%, #E9F2F7 100%);
  height: 50vh;
}

/* 右侧内容为医生插画“让位”：医生宽 24vw + 间隔 2vw = 26vw */
.hero-card-pad {
  padding-left: 39.2vw;  /* ← 调这个数就能控制“离人物多近” */
}

/* 文案容器靠右并限制最大宽度（不自适应，仅固定占比） */
/* 2) 取消会把文字往右推的 margin-left；放大可用宽度 */
.hero-text-wrap {
  margin-left: 0;        /* 原来是 6vw，去掉才能更靠近人物 */
  width: 100%;
  padding-right: 1vw;
}

/* 渐变文字 + 固定字号/行高/缩进（全部 vw/vh） */
.hero-text {
  font-weight: 600;
  font-size: 2.8vw;    /* 约等于原先 clamp 中位 */
  line-height: 8.0vh;  /* 行高随视口高 */
  text-indent: 4.8vw;
  background: linear-gradient(90deg, #4675EA 0%, #6AC4FF 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* 背景图：铺满屏幕 */
.bg-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 左上角 logo：固定位置与尺寸（vw） */
.logo {
  position: absolute;
  left: 2vw;
  top: 2vw;
  width: 8vw;
  height: auto;
  user-select: none;
}

/* 医生插画：固定宽度，按比例自适应高度；与右侧让位值一致 */
.doctor-illust {
  position: absolute;
  bottom: 0;
  left: 6vw;          /* 与让位的 2vw 间隔一致 */
  width: 32vw;        /* 医生主宽度 */
  height: 90vh;   /* 不超过视口高度 */
  object-fit: contain;
  filter: drop-shadow(0 2vh 1.3vh rgba(0, 0, 0, 0.25));
  z-index: 20;
  pointer-events: none;
  user-select: none;
}

/* 右上角测试面板：固定位置与尺寸（vw/vh） */
.test-panel {
  position: absolute;
  top: 2vh;
  right: 2vh;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 0.8vw;
  background: #fff;
  padding: 1vh 1.2vw;
  border-radius: 0.8vw;
  box-shadow: 0 0.6vh 1.2vh rgba(0,0,0,0.1);
  border: 0.1vw solid #e5e7eb;
}
.test-label {
  font-size: 0.9vw;
  line-height: 1.4vw;
  color: #4b5563;
}

.test-panel {
  position: absolute;
  top: 2vh;
  right: 2vh;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 0.8vw;
  background: #fff;
  padding: 1vh 1.2vw;
  border-radius: 0.8vw;
  box-shadow: 0 0.6vh 1.2vh rgba(0,0,0,0.1);
  border: 0.1vw solid #e5e7eb;
}

.test-label {
  font-size: 0.9vw;
  line-height: 1.4vw;
  color: #4b5563;
}

.patient-list-btn {
  margin-right: 0.4vw;
}
</style>
