<!-- frontend/src/views/HomePage.vue -->

<template>
  <div class="relative w-full min-h-screen overflow-hidden">

    <!-- 顶部区域（简洁版） -->
    <div
      class="absolute inset-x-0 top-0 bg-cover bg-center"
      :class="appStore.platform === 'phone' ? 'h-[44vh]' : 'h-1/2'"
      :style="{ backgroundImage: `url(${topBg})` }"
    >
      <div
        :class="[
          'absolute inset-x-[2.5vh] top-[2.8vh] rounded-2xl shadow-md overflow-hidden',
          appStore.platform === 'phone'
            ? 'h-[40vh] bg-white'
            : 'h-[46.3vh] bg-gradient-to-b from-[rgba(250,250,255,0.25)] to-[#E9F2F7]'
        ]"
      >
        <!-- 手机端：logo + 简短说明（朴素） -->
        <div v-if="appStore.platform === 'phone'" class="flex h-full flex-col">
          <div class="px-4 pt-3 pb-2 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <img class="h-7 w-auto" :src="logo" alt="logo" />
            </div>

            <!-- ====== phone test_input（需要可注释此块，不影响布局） ====== -->
            <div class="flex items-center gap-2 bg-white px-2 py-1 rounded border border-gray-200">
              <span class="text-[11px] text-gray-600">TEST</span>
              <el-input
                ref="testInput"
                v-model="inputCode"
                placeholder="输入 code"
                size="small"
                @keyup.enter.native="handleInput(inputCode)"
                style="width: 140px"
              />
              <el-button type="primary" size="small" @click="handleInput(inputCode)">确认</el-button>
            </div>
            <!-- ====== /phone test_input ====== -->
          </div>

          <div class="px-4 mt-2">
            <h1 class="text-[4.6vw] leading-tight text-gray-900 font-medium">开始信息采集</h1>
            <p class="mt-2 text-[3.6vw] leading-snug text-gray-600">
              为提升诊疗效率，请按步骤完成必要信息采集。
            </p>
          </div>

          <div class="mt-auto px-4 pb-3">
            <div class="flex items-center gap-2">
              <div class="h-1.5 flex-1 rounded-full bg-gray-200">
                <div class="h-full w-1/4 rounded-full bg-blue-500"></div>
              </div>
              <span class="text-[11px] text-gray-500">步骤 1 / 4</span>
            </div>
          </div>
        </div>

        <!-- 桌面端：沿用原效果（朴素保留） -->
        <div v-else>
          <img class="w-[7vw] h-[9vh] mt-[2vh] ml-[2.4vh]" :src="logo" alt="logo" />
          <img class="absolute top-[10vh] left-[27.5vw] w-[64.6vw] h-[5vh]" :src="titleSvg" alt="welcome-text01" />
          <p class="absolute top-[18vh] left-[38vw] w-[47vw] text-[1.6vw] text-blue-800">
            在这里我们将提前收集您的就诊信息，以协助专家诊疗，下面请您跟着我们的指令，开始吧!
          </p>
          <img class="absolute bottom-[2vh] left-[38vw] w-[28vw] h-[14vh]" :src="bubble" alt="welcome-text03" />

          <!-- ====== desktop test_input（需要可注释此块，不影响布局） ====== -->
          <div
            class="absolute top-[1.6vh] right-[1.6vh] z-20 flex items-center gap-2
                   bg-white px-3 py-2 rounded-lg shadow border border-gray-200"
          >
            <span class="text-xs text-gray-600">TEST</span>
            <el-input
              ref="testInput"
              v-model="inputCode"
              placeholder="输入 code"
              size="small"
              @keyup.enter.native="handleInput(inputCode)"
              style="width: 180px"
            />
            <el-button type="primary" size="small" @click="handleInput(inputCode)">确认</el-button>
          </div>
          <!-- ====== /desktop test_input ====== -->
        </div>
      </div>
    </div>

    <!-- 底部区域 -->
    <div
      class="absolute inset-x-0 bottom-0 bg-gradient-to-b from-[rgba(249,251,255,0.50)] to-transparent px-[3.4vw] flex justify-between items-start gap-2.5 p-6"
      :class="appStore.platform === 'phone' ? 'h-[56vh]' : 'h-1/2'"
    >
      <!-- 卡片：phone 用 4 行等分，desktop 四列 -->
      <div
        :class="appStore.platform === 'phone'
          ? 'w-full h-full grid grid-rows-4 gap-3'
          : 'w-full mt-[7.2vh] grid grid-cols-4 gap-2.5'"
      >
        <!-- STEP 1 -->
        <a
          :href="appStore.platform === 'phone' ? '/#/chat?platform=phone' : '/#/chat'"
          class="step-card bg-white rounded-2xl shadow hover:scale-105 transform transition"
          :class="appStore.platform === 'phone'
            ? 'h-full flex items-center gap-3 p-3'
            : 'flex-1 max-w-[21.4vw]'"
        >
          <img src="@/assets/AI预问诊@2x.png"
               :class="appStore.platform === 'phone' ? 'w-[24vw] h-auto rounded-lg' : 'w-full rounded-t-2xl'"
               alt="step1" />
          <div :class="appStore.platform === 'phone' ? 'min-w-0' : 'pl-4 pb-4'">
            <h3 :class="appStore.platform === 'phone' ? 'text-blue-600 text-base' : 'text-blue-600 text-xl mt-2'">STEP 1</h3>
            <p :class="appStore.platform === 'phone' ? 'text-gray-800 text-sm truncate' : 'text-gray-800'">AI 预问诊</p>
          </div>
        </a>

        <!-- STEP 2 -->
        <div
          class="step-card bg-white rounded-2xl shadow hover:scale-105 transform transition"
          :class="appStore.platform === 'phone'
            ? 'h-full flex items-center gap-3 p-3'
            : 'flex-1 max-w-[21.4vw]'"
        >
          <img src="@/assets/把脉@2x.png"
               :class="appStore.platform === 'phone' ? 'w-[24vw] h-auto rounded-lg' : 'w-full rounded-t-2xl'"
               alt="step2" />
          <div :class="appStore.platform === 'phone' ? 'min-w-0' : 'pl-4 pb-4'">
            <h3 :class="appStore.platform === 'phone' ? 'text-blue-600 text-base' : 'text-blue-600 text-xl mt-2'">STEP 2</h3>
            <p :class="appStore.platform === 'phone' ? 'text-gray-800 text-sm truncate' : 'text-gray-800'">中医舌脉信息采集指引</p>
          </div>
        </div>

        <!-- STEP 3 -->
        <div
          class="step-card bg-white rounded-2xl shadow hover:scale-105 transform transition"
          :class="appStore.platform === 'phone'
            ? 'h-full flex items-center gap-3 p-3'
            : 'flex-1 max-w-[21.4vw]'"
        >
          <img src="@/assets/血压采集@2x.png"
               :class="appStore.platform === 'phone' ? 'w-[24vw] h-auto rounded-lg' : 'w-full rounded-t-2xl'"
               alt="step3" />
          <div :class="appStore.platform === 'phone' ? 'min-w-0' : 'pl-4 pb-4'">
            <h3 :class="appStore.platform === 'phone' ? 'text-blue-600 text-base' : 'text-blue-600 text-xl mt-2'">STEP 3</h3>
            <p :class="appStore.platform === 'phone' ? 'text-gray-800 text-sm truncate' : 'text-gray-800'">身高体重血压信息采集指引</p>
          </div>
        </div>

        <!-- STEP 4 -->
        <div
          class="step-card bg-white rounded-2xl shadow hover:scale-105 transform transition"
          :class="appStore.platform === 'phone'
            ? 'h-full flex items-center gap-3 p-3'
            : 'flex-1 max-w-[21.4vw]'"
        >
          <img src="@/assets/生成报告.png"
               :class="appStore.platform === 'phone' ? 'w-[24vw] h-auto rounded-lg' : 'w-full rounded-t-2xl'"
               alt="step4" />
          <div :class="appStore.platform === 'phone' ? 'min-w-0' : 'pl-4 pb-4'">
            <h3 :class="appStore.platform === 'phone' ? 'text-blue-600 text-base' : 'text-blue-600 text-xl mt-2'">STEP 4</h3>
            <p :class="appStore.platform === 'phone' ? 'text-gray-800 text-sm truncate' : 'text-gray-800'">生成问诊报告智能辅助诊疗</p>
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
// ElMessageBox
import { useRouter, useRoute } from 'vue-router';

import { usePatientStore } from '@/stores/patient';
import { useAppStore } from '@/stores/app'; // 需包含 'phone' | 'app' | 'web'

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

/** 兼容 hash 路由 的查询解析（保留你的实现） */
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

/** 既兼容 search 又兼容 hash 的 query 聚合 */
function getAllQuery() {
  const fromRoute = route.query as Record<string, any>;
  const parsedHash = getQueryFromHash();
  const searchParams = new URLSearchParams(window.location.search || '');
  const parsedSearch: Record<string, string> = {};
  searchParams.forEach((v, k) => (parsedSearch[k] = v));
  // 优先顺序：route.query > search > hash
  return { ...parsedHash, ...parsedSearch, ...fromRoute } as Record<string, any>;
}

/** 根据 state 跳转（建议把你业务的 state 约定都统一到这里） */
function redirectByState(state: string | undefined) {
  const s = decodeURIComponent(state || '').trim();
  if (!s) {
    return; // 无 state 就不跳
  }
  // 1) 若以 / 开头，当成站内路由
  if (s.startsWith('/')) {
    const [path, q] = s.split('?', 2);
    const query: Record<string, string> = {};
    if (q) new URLSearchParams(q).forEach((v, k) => (query[k] = v));
    if (appStore.platform !== 'web') query.platform = appStore.platform;
    router.replace({ path, query }).catch(() => {});
    return;
  }
  // 2) 若是 http/https，当成外链
  if (/^https?:\/\//i.test(s)) {
    window.location.replace(s);
    return;
  }
  // 3) 其他情况：当成命名锚点或简单路径
  router.replace({ path: `/${s}` }).catch(() => {});
}

/** 向你自己的后端换取 openid（这里用 fetch，避免额外依赖） */
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
    // 存到 store（并持久化到 localStorage）
    await patientStore.recordScan("PID1234565").finally(() => toChat());; 
    // 把 openid 当作 patient_id 去获取数据

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

/** 从 URL 同步平台：支持 phone/app/web（默认 web） */
function syncPlatformFromUrl() {
  const fromRoute = route.query as Record<string, any>;
  const parsed = Object.keys(fromRoute || {}).length > 0 ? fromRoute : getQueryFromHash();
  const p = String(parsed.platform || '').toLowerCase();
  appStore.setPlatform(p); // 在 stores/app.ts 中确保支持 'phone'
}

/** 统一跳转 chat，并透传平台 */
function toChat(extraQuery: Record<string, any> = {}) {
  const q = { ...extraQuery };
  if (appStore.platform !== 'web') q.platform = appStore.platform;
  router.push({ path: '/phone/chat', query: q });
}

/** 扫码后的处理（保留你的实现） */
function handleScan(code: string) {
  const trimmed = (code || '').trim();
  if (!trimmed) return;
  patientStore.recordScan(trimmed).finally(() => {
    // 扫码后进入聊天
    setTimeout(() => toChat(), 300);
  });
  scanCode.value = '';
}

/** 手动输入测试（保留你的实现） */
function handleInput(code: string) {
  const trimmed = (code || '').trim();
  if (!trimmed) return;
  patientStore.recordScan(trimmed).finally(() => toChat());
}

onMounted(async () => {
  nextTick(() => scanInput.value?.focus());
  syncPlatformFromUrl();

  // （可保留）URL 参数提示
  try {
    const fromRoute = route.query as Record<string, any>;
    const parsed = Object.keys(fromRoute || {}).length > 0 ? fromRoute : getQueryFromHash();
    const rawHash = window.location.hash || '';
    const rawSearch = window.location.search || '';
    if (Object.keys(parsed).length > 0 || rawHash || rawSearch) {
      const lines: string[] = [];
      for (const [k, v] of Object.entries(parsed)) lines.push(`${k}: ${Array.isArray(v) ? v.join(', ') : (v ?? '')}`);
      // const msg =
      //   `原始地址片段（hash）：${rawHash || '(无)'}\n` +
      //   `原始查询串（search）：${rawSearch || '(无)'}\n\n` +
      //   `解析结果：\n${lines.length ? lines.join('\n') : '(无查询参数)'}`;
      // ElMessageBox.alert(msg.replace(/\n/g, '<br/>'), 'URL 参数', { dangerouslyUseHTMLString: true });
    }
  } catch (e) {
    console.error('解析 URL 查询参数失败：', e);
  }

  // ========= 新增：检测 code/state 并换取 openid =========
  try {
    if (!hasTriedExchange.value) {
      hasTriedExchange.value = true;

      const allQuery = getAllQuery();
      const code = String(allQuery.code || '').trim();
      // const state = String(allQuery.state || '').trim();

      if (code) {
        await exchangeCodeForOpenId(code);
        // redirectByState(state); // 如需按 state 跳转可开启
      }
    }
  } catch (e) {
    // 失败则不跳转，留在当前页或由用户手动操作
  }
  // ========= /新增：检测 code/state 并换取 openid =========

  // App 自定义扫码事件（保留你的实现）
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

  // 绑定扫码监听（保留）
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

// 资源（保留）
const topBg = topBgUrl;
const logo = logoUrl;
const titleSvg = titleSvgUrl;
const bubble = bubbleUrl;

// ========= 可选：暴露方法（如需在组件外触发） =========
defineExpose({
  exchangeCodeForOpenId,
  redirectByState
});
</script>
