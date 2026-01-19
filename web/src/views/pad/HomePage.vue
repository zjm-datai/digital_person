<!-- frontend/src/views/HomePage.vue -->

<template>
  <div class="home-page" :class="`platform-${appStore.platform}`">
    <!-- 顶部背景 + 医生图 -->
    <div class="background-layer">
      <div
        class="background-image"
        :style="{ backgroundImage: `url(${topBg})` }"
      ></div>

      <img
        src="@/assets/医生@2x.png"
        class="doctor-image"
        alt="Doctor"
      />
    </div>

    <!-- 顶部内容区域（PC & 手机共用外层） -->
    <div class="hero-overlay">
      <!-- 非手机：大卡片 -->
      <div v-if="appStore.platform !== 'phone'" class="hero-card-desktop">
        <img class="hero-logo-desktop" :src="logo" alt="logo" />
        <img class="hero-title-desktop" :src="titleSvg" alt="welcome" />
        <p class="hero-desc-desktop">
          在这里我们将提前收集您的就诊信息，以协助专家诊疗，下面请您跟着我们的指令，开始吧!
        </p>
        <img
          class="hero-bubble-desktop"
          :src="bubble"
          alt="start"
        />
      </div>

      <!-- 手机：顶部 info + 进度 -->
      <div v-else class="hero-card-phone">
        <div class="hero-phone-topbar">
          <div class="hero-phone-logo-wrap">
            <img class="hero-phone-logo" :src="logo" alt="logo" />
          </div>
          <div class="hero-phone-testbox">
            <span class="hero-phone-test-label">TEST</span>
            <el-input
              ref="testInput"
              v-model="inputCode"
              placeholder="输入 code"
              size="small"
              @keyup.enter.native="handleInput(inputCode)"
              style="width: 140px"
            />
            <el-button
              type="primary"
              size="small"
              @click="handleInput(inputCode)"
            >
              确认
            </el-button>
          </div>
        </div>

        <div class="hero-phone-text">
          <h1 class="hero-phone-title">开始信息采集</h1>
          <p class="hero-phone-subtitle">
            为提升诊疗效率，请按步骤完成必要信息采集。
          </p>
        </div>

        <div class="hero-phone-progress">
          <div class="hero-phone-progress-bar">
            <div class="hero-phone-progress-bar-inner"></div>
          </div>
          <span class="hero-phone-progress-text">步骤 1 / 4</span>
        </div>
      </div>
    </div>

    <!-- 底部步骤区域 -->
    <div class="bottom-panel">
      <div class="steps-grid">
        <!-- STEP 1 -->
        <router-link
          :to="appStore.platform === 'phone'
            ? { path: '/welcome', query: { platform: 'phone' } }
            : { path: '/welcome', query: { platform: 'app' } }"
          class="step-card step-card-link"
        >
          <div class="step-card-image-wrapper">
            <img src="@/assets/AI预问诊@2x.png" class="step-card-image" alt="step1" />
          </div>

          <div class="step-card-body">
            <h3 class="step-card-title">
              <span class="step-card-title-dot"></span>
              STEP 1
            </h3>
            <p class="step-card-desc">AI 预问诊</p>
          </div>
        </router-link>

        <!-- STEP 2 -->
        <div class="step-card">
          <div class="step-card-image-wrapper">
            <img
              src="@/assets/设备操作指引@2x.png"
              class="step-card-image"
              alt="step2"
            />
          </div>

          <div class="step-card-body">
            <h3 class="step-card-title">
              <span class="step-card-title-dot"></span>
              STEP 2
            </h3>
            <p class="step-card-desc">
              设备操作指引
            </p>
          </div>
        </div>

        <!-- STEP 3 -->
        <div class="step-card">
          <div class="step-card-image-wrapper">
            <img
              src="@/assets/问诊报告@2x.png"
              class="step-card-image"
              alt="step3"
            />
          </div>

          <div class="step-card-body">
            <h3 class="step-card-title">
              <span class="step-card-title-dot"></span>
              STEP 3
            </h3>
            <p class="step-card-desc">
              生成问诊报告<br />智能辅助诊疗
            </p>
          </div>
        </div>

        <!-- STEP 4 -->
        <div class="step-card">
          <div class="step-card-image-wrapper">
            <img
              src="@/assets/健康宣教@2x.png"
              class="step-card-image"
              alt="step4"
            />
          </div>

          <div class="step-card-body">
            <h3 class="step-card-title">
              <span class="step-card-title-dot"></span>
              STEP 4
            </h3>
            <p class="step-card-desc">
              个性健康宣教
            </p>
          </div>
        </div>
      </div>
    </div>

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
import { useAppStore } from '@/stores/app';

import topBgUrl from '@/assets/问诊页面最上方背景图.png';
import logoUrl from '@/assets/logo@2x.png';
import titleSvgUrl from '@/assets/标题@3x.svg';
import bubbleUrl from '@/assets/气泡@2x.png';

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
      obj[k] = Array.isArray(obj[k])
        ? [...(obj[k] as string[]), v]
        : [obj[k] as string, v];
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

function redirectByState(state: string | undefined) {
  const s = decodeURIComponent(state || '').trim();
  if (!s) {
    return;
  }
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
    await patientStore.recordScan('PID1234563').finally(() => toChat());

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

function syncPlatformFromUrl() {
  const fromRoute = route.query as Record<string, any>;
  const parsed =
    Object.keys(fromRoute || {}).length > 0 ? fromRoute : getQueryFromHash();
  const p = String(parsed.platform || '').toLowerCase();
  appStore.setPlatform(p);
}

function toChat(extraQuery: Record<string, any> = {}) {
  const q = { ...extraQuery };
  if (appStore.platform !== 'web') q.platform = appStore.platform;
  router.push({ path: '/chat', query: q });
}

function handleScan(code: string) {
  const trimmed = (code || '').trim();
  if (!trimmed) return;
  patientStore.recordScan(trimmed).finally(() => {
    setTimeout(() => toChat(), 300);
  });
  scanCode.value = '';
}

function handleInput(code: string) {
  const trimmed = (code || '').trim();
  if (!trimmed) return;
  patientStore.recordScan(trimmed).finally(() => toChat());
}

onMounted(async () => {
  nextTick(() => scanInput.value?.focus());
  syncPlatformFromUrl();

  try {
    const fromRoute = route.query as Record<string, any>;
    const parsed =
      Object.keys(fromRoute || {}).length > 0 ? fromRoute : getQueryFromHash();
    const rawHash = window.location.hash || '';
    const rawSearch = window.location.search || '';
    if (Object.keys(parsed).length > 0 || rawHash || rawSearch) {
      const lines: string[] = [];
      for (const [k, v] of Object.entries(parsed)) {
        lines.push(
          `${k}: ${Array.isArray(v) ? v.join(', ') : (v ?? '')}`
        );
      }
      // 原来的弹窗提示已注释
    }
  } catch (e) {
    console.error('解析 URL 查询参数失败：', e);
  }

  try {
    if (!hasTriedExchange.value) {
      hasTriedExchange.value = true;

      const allQuery = getAllQuery();
      const code = String(allQuery.code || '').trim();
      // const state = String(allQuery.state || '').trim();

      if (code) {
        await exchangeCodeForOpenId(code);
        // redirectByState(state);
      }
    }
  } catch (e) {
    // 失败则不跳转
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
      ElNotification({
        message: `扫码内容：${code}`,
        type: 'success',
        position: 'top-right',
        duration: 2000,
        showClose: true
      });
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

watch(
  () => route.fullPath,
  () => syncPlatformFromUrl()
);

onBeforeUnmount(() => {
  onScan.detachFrom(document);
});

const topBg = topBgUrl;
const logo = logoUrl;
const titleSvg = titleSvgUrl;
const bubble = bubbleUrl;

defineExpose({
  exchangeCodeForOpenId,
  redirectByState
});
</script>

<style scoped>
/* 整体页面 */
.home-page {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
}

/* 背景层 */
.background-layer {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.background-image {
  position: absolute;
  inset: 0;
  width: 100%;
  overflow: hidden;
  background-size: cover;
  background-position: center;
}

/* 不同平台下背景高度 */
.platform-phone .background-image {
  height: 43vh;
}

.platform-app .background-image,
.platform-web .background-image,
.platform-undefined .background-image {
  height: 50vh;
}

/* 医生图 */
.doctor-image {
  position: absolute;
  bottom: 0;
  left: 3vw;
  height: 90vh;
  width: auto;
  object-fit: cover;
  object-position: top;
  z-index: 0;
  pointer-events: none;
  filter: drop-shadow(0 12px 24px rgba(0, 0, 0, 0.25));
}

/* 顶部内容 overlay */
.hero-overlay {
  position: absolute;
  left: 2.5vh;
  right: 2.5vh;
  top: 2.8vh;
  z-index: 10;
  pointer-events: none;
}

/* 不同平台下 overlay 高度 */
.platform-phone .hero-overlay {
  height: 41vh;
}

.platform-app .hero-overlay,
.platform-web .hero-overlay,
.platform-undefined .hero-overlay {
  height: 48vh;
}

/* 桌面端顶部卡片 */
.hero-card-desktop {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 1rem 1rem 0 0;
  border: 2px solid #ffffff;
  background: transparent;
  pointer-events: none;
}

.hero-logo-desktop {
  position: absolute;
  top: 2vh;
  left: 2.4vh;
  width: 10vh;
  height: 8vh;
  object-fit: contain;
}

.hero-title-desktop {
  position: absolute;
  top: 10vh;
  left: 27.5vw;
  width: 64.6vw;
  height: 5vh;
  object-fit: contain;
}

.hero-desc-desktop {
  position: absolute;
  top: 18vh;
  left: 30.5vw;
  width: 60vw;
  font-size: 1.8vw;
  line-height: 1.6;
  color: #1d4ed8; /* 蓝色 */
  font-weight: 500;
}

.hero-bubble-desktop {
  position: absolute;
  bottom: 2vh;
  left: 38vw;
  width: 28vw;
  height: 14vh;
  object-fit: contain;
  pointer-events: auto;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.hero-bubble-desktop:hover {
  transform: scale(1.05);
}

/* 手机端顶部卡片 */
.hero-card-phone {
  display: flex;
  flex-direction: column;
  height: 100%;
  pointer-events: auto;
}

/* 顶部栏 */
.hero-phone-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem 0.5rem;
}

.hero-phone-logo-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-phone-logo {
  height: 1.5rem;
  width: auto;
}

.hero-phone-testbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #ffffff;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.hero-phone-test-label {
  font-size: 11px;
  color: #4b5563;
}

/* 手机文字区 */
.hero-phone-text {
  padding: 0.5rem 1rem 0;
  margin-top: 0.5rem;
}

.hero-phone-title {
  font-size: 4.6vw;
  color: #111827;
  font-weight: 500;
  margin: 0;
}

.hero-phone-subtitle {
  margin-top: 0.5rem;
  font-size: 3.6vw;
  color: #4b5563;
}

/* 手机进度条 */
.hero-phone-progress {
  margin-top: auto;
  padding: 0 1rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-phone-progress-bar {
  height: 6px;
  flex: 1;
  border-radius: 999px;
  background-color: #e5e7eb;
  overflow: hidden;
}

.hero-phone-progress-bar-inner {
  height: 100%;
  width: 25%;
  border-radius: 999px;
  background-color: #3b82f6;
}

.hero-phone-progress-text {
  font-size: 11px;
  color: #6b7280;
}

/* 底部步骤 panel */
.bottom-panel {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.6),
    rgba(255, 255, 255, 0.8),
    #ffffff
  );
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 -10px 40px rgba(255, 255, 255, 0.6);
  transition: all 0.5s ease;
}

/* 不同平台下 bottom-panel 高度/对齐 */
.platform-phone .bottom-panel {
  height: 56vh;
  align-items: flex-start;
  padding-top: 2.5rem;
}

.platform-app .bottom-panel,
.platform-web .bottom-panel,
.platform-undefined .bottom-panel {
  height: 50vh;
  align-items: center;
}

/* 步骤网格 */
.steps-grid {
  width: 100%;
  display: grid;
  gap: 1rem;
}

/* 手机：4 行 */
.platform-phone .steps-grid {
  grid-template-rows: repeat(4, 1fr);
}

/* 桌面：4 列 */
.platform-app .steps-grid,
.platform-web .steps-grid,
.platform-undefined .steps-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

/* 单个 step 卡片 */
.step-card {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 1rem;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.6);
  display: flex;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

/* 桌面卡片布局为纵向 */
.platform-app .step-card,
.platform-web .step-card,
.platform-undefined .step-card {
  flex-direction: column;
  height: 100%;
}

/* 手机卡片：横向对齐 */
.platform-phone .step-card {
  flex-direction: row;
  align-items: center;
  padding: 0.75rem;
}

/* hover 效果 */
.step-card:hover {
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
  transform: translateY(-4px);
}

/* STEP1 是 a 链接，样式与 div 一致 */
.step-card-link {
  text-decoration: none;
  color: inherit;
}

/* 图片容器 */
.step-card-image-wrapper {
  position: relative;
  overflow: hidden;
  flex: 0 0 auto;
}

/* 手机图片尺寸 */
.platform-phone .step-card-image-wrapper {
  width: 24vw;
  border-radius: 0.75rem;
  aspect-ratio: 16 / 9;
}

/* 桌面图片尺寸 */
.platform-app .step-card-image-wrapper,
.platform-web .step-card-image-wrapper,
.platform-undefined .step-card-image-wrapper {
  width: 100%;
  border-radius: 1rem 1rem 0 0;
  aspect-ratio: 16 / 9;
}

/* 图片本身 */
.step-card-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

/* hover 时图片放大 */
.step-card:hover .step-card-image {
  transform: scale(1.1);
}

/* 文本区域 */
.step-card-body {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

/* 手机文本区域 */
.platform-phone .step-card-body {
  min-width: 0;
  margin-left: 0.5rem;
}

/* 桌面文本区域 */
.platform-app .step-card-body,
.platform-web .step-card-body,
.platform-undefined .step-card-body {
  flex: 1;
  align-items: center;
  justify-content: flex-start;
  padding-top: 0.75rem;
  padding-bottom: 1rem;
}

/* 标题行 */
.step-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2563eb;
  font-weight: 700;
  margin: 0;
}

/* 手机标题大小 */
.platform-phone .step-card-title {
  font-size: 1rem;
}

/* 桌面标题大小 */
.platform-app .step-card-title,
.platform-web .step-card-title,
.platform-undefined .step-card-title {
  font-size: 1.25rem;
  margin-bottom: 0.75rem;
}

/* 小圆点 */
.step-card-title-dot {
  display: inline-block;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 999px;
  background-color: #3b82f6;
}

/* 描述文本 */
.step-card-desc {
  margin: 0;
  text-align: center;
  font-weight: 700;
  color: #1f2933;
}

/* 手机描述 */
.platform-phone .step-card-desc {
  font-size: 0.875rem;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 桌面描述 */
.platform-app .step-card-desc,
.platform-web .step-card-desc,
.platform-undefined .step-card-desc {
  font-size: 1.125rem;
  line-height: 1.5;
  min-height: 3rem;
}

/* 简单的自适应：小屏 padding 缩小一点 */
@media (max-width: 640px) {
  .bottom-panel {
    padding: 1.5rem 1rem;
  }
}
</style>
