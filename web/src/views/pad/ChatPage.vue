<template>
  <div class="page-root">
    <!-- 顶部区域 -->
    <div id="top-area" class="top-area">
      <img
        src="/src/assets/问诊页面最上方背景图.png"
        class="cover-img"
        alt="banner"
      />

      <!-- 顶部栏：logo + 病人信息 -->
      <div class="topbar">
        <!-- logo -->
        <img src="/public/logo@2x.png" class="logo" alt="logo" />

        <!-- 病人信息区域：占据剩余宽度 -->
        <div id="patient-info" class="patient-info">
          <div class="patient-row">
            <!-- 患者姓名 -->
            <div class="patient-item">
              <User class="icon-xxl icon-strong" />
              <span>患者姓名：<span class="text-strong">{{ patient.name }}</span></span>
            </div>

            <!-- 年龄 -->
            <div class="patient-item">
              <Calendar class="icon-xxl icon-dim" />
              <span>年龄：<span class="text-strong">{{ patient.age }}</span></span>
            </div>

            <!-- 科室 -->
            <div class="patient-item">
              <Stethoscope class="icon-xxl icon-dim" />
              <span>挂号科室：<span class="text-strong">{{ patient.department }}</span></span>
            </div>
          </div>
        </div>

        <!-- 右侧喇叭按钮（与截图一致，仅图标） -->
        <button
          class="speaker-btn"
          :title="isAudioing ? '关闭播报' : '开启播报'"
          aria-label="语音播报控制"
          @click="toggleAudio"
        >
          <component :is="isAudioing ? VolumeXIcon : AudioWaveformIcon" class="speaker-icon" />
        </button>
      </div>
    
    </div>

    <!-- 进度条区域 -->
    <div id="process-area" class="process-area">
      <div class="process-inner">
        <div class="process-row">
          <!-- 左侧标题 -->
          <div class="process-title">
            <span>答题进度 </span>
            <span class="process-current">{{ current }}</span>
            <span class="process-total">/{{ total }}</span>
          </div>

          <!-- 进度条 -->
          <div class="progress">
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{ width: percent + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主体区域 -->
    <div id="main-area" class="main-area">
      <!-- 医生立绘区域 -->
      <div id="doctorpic-area" class="doctor-area">
        <img
          src="/医生@2x.png"
          class="doctor-img"
          alt="doctor"
          draggable="false"
        />
      </div>

      <!-- 问答区域 -->
      <div class="qa-area">
        <div id="chat-area" class="chat-area">
          <!-- 只循环一次：每条消息下方按 role 分支渲染外置按钮 -->
          <div
            v-for="(msg, idx) in qaWindow"
            :key="`qa-${idx}`"
            class="msg-block"
          >
            <!-- 气泡 -->
            <div class="msg-line" :class="msg.role === 'assistant' ? 'align-start' : 'align-end'">
              <div class="msg-bundle" :class="msg.role === 'assistant' ? '' : 'reverse'">
                <el-avatar
                  :src="msg.role === 'assistant' ? doctorAvatar : userAvatar"
                  size="large"
                  class="avatar"
                />
                <div
                  class="bubble"
                  :class="msg.role === 'assistant' ? 'bubble-assistant' : 'bubble-user'"
                >
                  <div class="bubble-text-lg">{{ msg.content }}</div>
                  <div v-if="msg.summary" class="bubble-text-md">{{ msg.summary }}</div>

                  <button
                    v-if="msg.role === 'assistant' && msg.summary"
                    @click="handleSummaryClick"
                    class="btn-link"
                  >
                    🌟 查看总结报告
                  </button>
                </div>
              </div>
            </div>

            <!-- 外置按钮行：跟随该条气泡，按 role 渲染 -->
            <!-- 1) assistant：推荐回答（去重后） -->
            <transition-group name="pop" tag="div" appear>
              <div
                v-if="msg.role === 'assistant' && isLatestRound && dedupeArray(msg.suggestions || []).length"
                class="btnline btnline-left"
              >
                <div class="btnline-wrap btnline-wrap-left">
                  <div class="chips">
                    <button
                      v-for="(s, i) in dedupeArray(msg.suggestions || [])"
                      :key="`sug-${idx}-${i}`"
                      class="chip-btn"
                      @click="onSuggestionClick(s)"
                    >
                      {{ s }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- 2) user：仅当该条为当前锚定用户消息时，显示接近选项 + 重新输入 -->
              <div
                v-if="msg.role === 'user' && isLatestRound && isAnchor(msg)"
                class="btnline btnline-right"
              >
                <div class="btnline-wrap btnline-wrap-right">
                  <div class="chips">
                    <button
                      v-for="(opt, i) in nearestOptions"
                      :key="`near-${idx}-${i}`"
                      class="chip-btn"
                      @click="onPickNearest(opt)"
                    >
                      {{ opt.label }}
                    </button>

                    <button
                      class="chip-btn"
                      @click="onRetryInput"
                    >
                      重新输入
                    </button>
                  </div>
                </div>
              </div>
              <!-- 其他情况：不渲染外置按钮 -->
            </transition-group>
          </div>
        </div>

        <!-- 输入控制区域 -->
        <div id="chat-control" class="chat-control">
          <!-- 上一题（仅在非录音态显示） -->
          <template v-if="!isRecording">
            <button class="nav-btn" @click="handlePrev">
              <ChevronLeft class="icon-sm" />
              上一题
            </button>
          </template>

          <!-- 中间：语音识别条 / 输入模式 / 录音模式 -->
          <div
            class="center-control"
            :class="isRecording ? '' : 'center-control-boxed'"
          >
            <!-- 非输入、非录音 -->
            <template v-if="!isTypingMode && !isRecording">
              <div class="center-hint" @click="startRecordingUI">
                点击进入语音识别
              </div>
              <button
                class="icon-btn"
                @click="isTypingMode = true; $nextTick(() => inputRef?.focus())"
                :title="'切换到键盘输入'"
              >
                <Keyboard class="icon-md icon-dim" />
              </button>
            </template>

            <!-- 文本输入模式 -->
            <template v-else-if="isTypingMode">
              <input
                ref="inputRef"
                v-model="inputValue"
                type="text"
                :placeholder="'请输入内容...'"
                class="text-input"
                @keydown.enter.prevent="sendInput"
              />
              <div class="center-actions">
                <button
                  class="icon-btn"
                  @click="isTypingMode = false"
                  :title="'返回语音模式'"
                >
                  <Mic class="icon-md icon-dim" />
                </button>
                <button class="send-btn" @click="sendInput">
                  <div class="send-btn-inner">
                    <Send class="icon-xs" />
                  </div>
                </button>
              </div>
            </template>

            <!-- 录音模式 -->
            <template v-else>
              <div class="recording-row">

                <div class="recording-center">
                  <div class="recording-timer">
                    <span class="timer-dim">正在录音，</span>
                    <span class="timer-strong">{{ remainSeconds }}s</span>
                    <span class="timer-dim"> 后停止录音</span>
                  </div>

                  <div class="wave-box">
                    <div class="wave-bars">
                      <span v-for="i in 24" :key="i" class="wave-bar"></span>
                    </div>
                  </div>
                </div>

                <button class="control-btn" @click="endRecordingUI">
                  <Send class="icon-xs" />
                  结束录音
                </button>
              </div>
            </template>
          </div>

          <!-- 下一题 -->
          <template v-if="!isRecording">
            <button
              class="nav-btn"
              @click="handleNext"
              :disabled="isLatestRound && !hasUserInCurrentRound"
            >
              下一题
              <ChevronRight class="icon-sm" />
            </button>
          </template>
        </div>
      </div>
    </div>

    <WebsocketTTS />
  </div>
</template>

<script setup lang="ts">
/* =========================
 * Imports
 * ========================= */
import { ref, computed, reactive, watchEffect, onMounted, watch, onBeforeUnmount } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElNotification } from "element-plus";
import {
  User, Calendar, Stethoscope, Keyboard, Mic, Send,
  ChevronLeft, ChevronRight,
  VolumeXIcon, AudioWaveformIcon
} from "lucide-vue-next";

import doctorAvatar from "@/assets/doctor.svg";
import userAvatar from "@/assets/patient.svg";

import { useAudioRecorder } from "@/composables/useAudioRecorder";
import { useChatStream } from "@/composables/useChatStream";

import { storeToRefs } from "pinia";
import { usePatientStore } from "@/stores/patient";
import { useChatHistoryStore } from "@/stores/chatHistory";
import { useSummaryStore } from "@/stores/summary";

import type { ChatMessage } from "@/types/web/chat";

import WebsocketTTS from "@/components/WebsocketTTS.vue";
import { ttsBus } from "@/bus/ttsBus";

import { getChatMessages } from "@/api/chat";

/* =========================
 * Stores & Refs
 * ========================= */
const router = useRouter();
const route = useRoute();

const chatHistory = useChatHistoryStore();
const { messages } = storeToRefs(chatHistory);

const patientStore = usePatientStore();
const { base, detail } = storeToRefs(patientStore);

const summaryStore = useSummaryStore();

const sid = ref<string | null>(
  typeof route.query.sid === "string"
    ? route.query.sid
    : Array.isArray(route.query.sid)
      ? route.query.sid[0]
      : null
);

/* =========================
 * UI State
 * ========================= */
const overwriteTargetId = ref<string | null>(null);

const isTypingMode = ref(false);
const inputValue = ref("");
const inputRef = ref<HTMLInputElement | null>(null);

/* Recording */
const isPaused = ref(false);
const remainSeconds = ref(60);
let timer: number | null = null;

/* App env */
const isApp = ref<boolean>(Boolean((window as any).uni));

/* Anchor & options */
const actionAnchorId = ref<string | null>(null);
const nearestOptions = ref<{ label: string; value: string }[]>([]);

/* Rounds & windows */
const roundPtr = ref(0);
const assistantIdxList = computed(() => {
  const out: number[] = [];
  messages.value.forEach((m, i) => { if (m.role === "assistant") out.push(i); });
  return out;
});
const roundRange = computed(() => {
  const list = assistantIdxList.value;
  if (!list.length) return { start: 0, end: messages.value.length };
  const k = Math.min(roundPtr.value, list.length - 1);
  const start = list[list.length - 1 - k];
  const nextStart = list[list.length - k] ?? messages.value.length;
  return { start, end: nextStart };
});
const qaWindow = computed(() => {
  if (!messages.value.length) return [];
  const { start, end } = roundRange.value;
  return messages.value.slice(start, end);
});
const isLatestRound = computed(() => roundPtr.value === 0);
const hasUserInCurrentRound = computed(() => {
  const { start, end } = roundRange.value;
  for (let i = start; i < end; i++) if (messages.value[i]?.role === "user") return true;
  return false;
});

/* =========================
 * Patient basic info (fallback)
 * ========================= */
const patient = reactive({
  name: "刘德华",
  gender: "男",
  age: 55,
  caseNo: "assd",
  department: "皮肤科",
});

/* =========================
 * Progress UI (来自 useChatStream)
 * ========================= */
const progress = ref<{ completed: number; total: number }>({ completed: 0, total: 0 });
const total = computed(() => progress.value.total || 0);
const current = computed(() => Math.min(progress.value.completed || 0, total.value));
const percent = computed(() => total.value ? Math.min(100, Math.max(0, (current.value / total.value) * 100)) : 0);

/* =========================
 * History
 * ========================= */
const historyLoaded = ref(false);

async function loadHistory(conversationId: string) {
  try {
    const appType = normalizeAppTypeFromDepartment(patient.department || "");
    const list = await getChatMessages({ conversationId, appType });

    messages.value = list;

    roundPtr.value = 0;
    syncAnchorForLatestRound();
  } catch (err) {
    console.error("loadHistory 出错：", err);
    messages.value = [];
  } finally {
    historyLoaded.value = true;
  }
}


/* =========================
 * 科室 -> app_type 映射（与你 welcome 页一致）
 * ========================= */
function normalizeAppTypeFromDepartment(dept: string) {
  const d = (dept || "").trim();
  const map: Record<string, string> = {
    "呼吸科": "huxike",
    "皮肤医美中心": "pifuke",
    "肛肠科": "gangchangke",
    "皮肤科": "pifuke",
  };
  return map[d] || "huxike";
}

/* =========================
 * TTS & Stream (新接口版 useChatStream)
 * ========================= */
const ttsText = ref("");
const ttsPlay = ref(false);

// 把 composable 的 progress 同步到本页面 progress（如果你 composable 已经返回 progress，直接解构使用也行）
const streamHook = useChatStream({
  messages,
  ttsText,
  ttsPlay,
  getConversationId: () => sid.value,
  getOpcId: () => patientStore.scanCode || "",
  getAppType: () => normalizeAppTypeFromDepartment(patient.department || ""),
});
/**
 * 你原来是 const { streamAnswer, progress } = useChatStream(...)
 * 但你现在上面已经调用一次了。为了不重复实例化，我这里建议你只保留一次。
 * 为了兼容你当前文件，我在下面做一次“就地修复”：只用第二次的实例（带 progress）。
 */
const _streamAnswer = streamHook.streamAnswer;
progress.value = streamHook.progress.value;
watch(streamHook.progress, (p) => (progress.value = p), { deep: true });

/* =========================
 * Audio recorder
 * ========================= */
const { isRecording, startRecording, stopRecording, handleReceiveAudio } = useAudioRecorder({
  isApp,
  onSTT(text: string) {
    const t = (text || "").trim();
    if (!t) return;

    if (overwriteTargetId.value) {
      const i = messages.value.findIndex(m => m.id === overwriteTargetId.value && m.role === "user");
      if (i !== -1) {
        messages.value[i].content = t;
        actionAnchorId.value = overwriteTargetId.value;
        overwriteTargetId.value = null;
        fetchNearestOptions(t);
        return;
      }
      overwriteTargetId.value = null;
    }

    appendUserMessage(t);
    fetchNearestOptions(t);
  }
});

/* =========================
 * Effects & Watchers
 * ========================= */
watchEffect(() => {
  if (base.value) {
    patient.name = base.value.name || "";
    patient.age = base.value.age || 0;
    patient.caseNo = (base.value as any).visit_number ?? "";
    patient.department = (base.value as any).department ?? "";
  }
});

/**
 * 首轮触发对话（新接口：需要 opc_id + app_type + conversation_id）
 */
watch(
  [() => detail.value, () => sid.value, () => historyLoaded.value, () => patientStore.scanCode],
  async ([newVal, curSid, loaded, opcId]) => {
    if (!loaded) return;
    if (messages.value.length > 0) return;      // 有历史就不触发首轮

    if (!newVal || !curSid) return;
    if (!opcId) return;

    messages.value.push({ role: "assistant", content: "", thinking: "" });
    const idx = messages.value.length - 1;

    _streamAnswer({
      messagesForApi: [{ role: "user", content: JSON.stringify(newVal), thinking: "" }],
      index: idx,
    }).catch(err => {
      console.error("第一次对话失败:", err);
      messages.value[idx].content = "[对话启动失败，请稍候重试]";
    });
  },
  { immediate: true }
);

/* 保存总结：防抖 & 去重 */
let saveTimer: number | null = null;
const DEBOUNCE_MS = 700;
let pendingSummary = "";
let lastCommitted = "";

watch(
  () => messages.value,
  (list) => {
    if (!Array.isArray(list) || !list.length) return;
    for (let i = list.length - 1; i >= 0; i--) {
      const m = list[i];
      if (m?.role === "assistant" && m.summary && String(m.summary).trim()) {
        const current = String(m.summary).trim();
        if (current === pendingSummary) break;
        pendingSummary = current;
        if (saveTimer) window.clearTimeout(saveTimer);
        saveTimer = window.setTimeout(() => {
          if (pendingSummary && pendingSummary !== lastCommitted) {
            summaryStore.setSummary({ text: pendingSummary, rawMessage: m });
            lastCommitted = pendingSummary;
            ElNotification({
              title: "已保存总结",
              message: "总结已在流式完成后保存。",
              type: "success",
              position: "top-right",
              duration: 1600,
            });
          }
          saveTimer = null;
        }, DEBOUNCE_MS);
        break;
      }
    }
  },
  { deep: true }
);

watch(roundPtr, (v) => {
  if (v === 0) syncAnchorForLatestRound();
});

/* =========================
 * Lifecycle
 * ========================= */
onMounted(async () => {
  sid.value = String(route.query.conversation_id || "").trim() || null;
  if (!sid.value) {
    router.push({ path: "/home" });
    return;
  }

  chatHistory.resetForSession(sid.value);

  if (sid.value) await loadHistory(sid.value);
  else historyLoaded.value = true;

  const hash = window.location.hash.split("?")[1] || "";
  const params = new URLSearchParams(hash);
  isApp.value = params.get("platform") === "app";

  if (isApp.value) {
    (window as any).receiveAudioFromApp = handleReceiveAudio;
    ElNotification({
      message: "app 端加载完成",
      type: "success",
      position: "top-right",
      duration: 2000,
      showClose: true,
    });
  }
});

onBeforeUnmount(() => {
  if (saveTimer) {
    window.clearTimeout(saveTimer);
    saveTimer = null;
  }
  stopTick();
  stopTTS();
});

/* =========================
 * Functions (UI actions)
 * ========================= */
function sendInput() {
  if (!isLatestRound.value) {
    ElNotification({ message: "当前在历史浏览，无法输入。请先回到最新一轮。", type: "info" });
    return;
  }
  const text = inputValue.value.trim();
  if (!text) return;
  appendUserMessage(text);
  inputValue.value = "";
  isTypingMode.value = false;
}

function handlePrev() {
  if (!assistantIdxList.value.length) return;
  const maxPtr = assistantIdxList.value.length - 1;
  if (roundPtr.value >= maxPtr) return;
  roundPtr.value += 1;
  actionAnchorId.value = null;
  resetInputUI();
}

function handleNext() {
  if (roundPtr.value > 0) {
    roundPtr.value = Math.max(0, roundPtr.value - 1);
    resetInputUI();
    if (roundPtr.value === 0) syncAnchorForLatestRound();
    return;
  }
  if (!hasUserInCurrentRound.value) return;

  let target: ChatMessage | undefined;
  if (actionAnchorId.value) {
    target = messages.value.find(m => m.id === actionAnchorId.value && m.role === "user");
  }
  if (!target) {
    const { start, end } = roundRange.value;
    for (let i = end - 1; i >= start; i--) {
      if (messages.value[i]?.role === "user") { target = messages.value[i]; break; }
    }
  }
  if (!target) return;
  sendForUserMessage(target);
}

function startRecordingUI() {
  if (!isLatestRound.value) {
    ElNotification({ message: "当前在历史浏览，无法录音。请先回到最新一轮。", type: "info" });
    return;
  }
  if (isRecording.value) return;

  stopTTS();

  isTypingMode.value = false;
  remainSeconds.value = 60;
  isPaused.value = false;
  startRecording();
  startTick();
}

function endRecordingUI() {
  if (!isRecording.value) return;
  stopTick();
  stopRecording();
}

function endRecording() {
  stopTick();
  isRecording.value = false;
  const transcript = "";
  if (transcript.trim()) messages.value.push({ role: "user", content: transcript.trim() });
}

function startTick() {
  stopTick();
  timer = window.setInterval(() => {
    if (isPaused.value) return;
    if (remainSeconds.value > 0) remainSeconds.value -= 1;
    else endRecording();
  }, 1000);
}

function stopTick() {
  if (timer !== null) { clearInterval(timer); timer = null; }
}

function isAnchor(msg: ChatMessage) {
  return Boolean(msg.id && actionAnchorId.value && msg.id === actionAnchorId.value);
}

function appendUserMessage(text: string) {
  stopTTS();

  const msg: ChatMessage = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    role: "user",
    content: text,
  };
  messages.value.push(msg);
  actionAnchorId.value = msg.id;
}

function onSuggestionClick(text: string) {
  if (!isLatestRound.value) {
    ElNotification({ message: "正在浏览历史记录，无法操作。请先返回最新一轮。", type: "warning" });
    return;
  }
  if (actionAnchorId.value) {
    const i = messages.value.findIndex(m => m.id === actionAnchorId.value && m.role === "user");
    if (i !== -1) {
      messages.value[i].content = text;
      sendForUserMessage(messages.value[i]);
      return;
    }
  }
  const msg: ChatMessage = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    role: "user",
    content: text,
  };
  messages.value.push(msg);
  actionAnchorId.value = msg.id;
  sendForUserMessage(msg);
}

function handleSummaryClick() {
  stopTTS();
  router.push("/report");
}

function onPickNearest(opt: { label: string; value: string }) {
  if (!isLatestRound.value) {
    ElNotification({ message: "正在浏览历史记录，无法操作。请先返回最新一轮。", type: "warning" });
    return;
  }
  if (!actionAnchorId.value) return;
  const idx = messages.value.findIndex(m => m.id === actionAnchorId.value && m.role === "user");
  if (idx === -1) return;
  messages.value[idx].content = opt.label;
  sendForUserMessage(messages.value[idx]);
}

function syncAnchorForLatestRound() {
  if (!isLatestRound.value) return;
  const { start, end } = roundRange.value;
  let lastUser: ChatMessage | undefined;
  for (let i = end - 1; i >= start; i--) {
    const m = messages.value[i];
    if (m?.role === "user") { lastUser = m; break; }
  }
  actionAnchorId.value = lastUser?.id ?? null;
}

function resetInputUI() {
  isTypingMode.value = false;
  if (isRecording.value) {
    stopTick();
    isRecording.value = false;
  }
  nearestOptions.value = [];
}

function onRetryInput() {
  if (!isLatestRound.value) {
    ElNotification({ message: "正在浏览历史记录，无法操作。请先返回最新一轮。", type: "warning" });
    return;
  }
  if (!actionAnchorId.value) return;

  const idx = messages.value.findIndex(m => m.id === actionAnchorId.value && m.role === "user");
  if (idx === -1) return;

  messages.value[idx].content = "";
  nearestOptions.value = [];
  isTypingMode.value = false;
  overwriteTargetId.value = actionAnchorId.value;

  startRecordingUI();
}

function dedupeArray(arr: string[]) {
  const set = new Set<string>();
  const out: string[] = [];
  for (const s of arr) { if (!set.has(s)) { set.add(s); out.push(s); } }
  return out;
}

function withTimeout<T>(p: Promise<T>, ms = 15000): Promise<T> {
  return new Promise((resolve, reject) => {
    const id = setTimeout(() => reject(new Error("Request timeout")), ms);
    p.then(
      v => { clearTimeout(id); resolve(v); },
      e => { clearTimeout(id); reject(e); }
    );
  });
}

type NearestOption = { label: string; value: string };
async function fetchNearestOptions(asrText: string) {
  try {
    if (!asrText?.trim()) {
      nearestOptions.value = [];
      return;
    }
    const url = new URL("/console_app/asr/suggest", window.location.origin);
    url.searchParams.set("asr", asrText);
    url.searchParams.set("k", "3");
    url.searchParams.set("locale", "zh");
    const resp = await withTimeout(
      fetch(url.toString(), { method: "GET", headers: { Accept: "application/json" }, credentials: "include" }),
      15000
    );
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    const arr: NearestOption[] = Array.isArray(data) ? data : data?.options || [];
    const seen = new Set<string>();
    nearestOptions.value = arr
      .filter(x => x && x.label && x.value)
      .filter(x => { const key = `${x.label}|||${x.value}`; if (seen.has(key)) return false; seen.add(key); return true; })
      .slice(0, 8);
  } catch (err) {
    console.error("fetchNearestOptions failed:", err);
    nearestOptions.value = [];
    ElNotification({ message: "获取推荐选项失败", type: "warning" });
  }
}

function sendForUserMessage(userMsg: ChatMessage) {
  stopTTS();

  messages.value.push({ role: "assistant", content: "", thinking: "" });
  const idx = messages.value.length - 1;

  actionAnchorId.value = null;
  nearestOptions.value = [];

  _streamAnswer({
    messagesForApi: [{ role: "user", content: userMsg.content, thinking: "" }],
    index: idx,
  }).catch(err => {
    console.error("发送失败:", err);
    messages.value[idx].content = "[发送失败，请重试]";
  });

  roundPtr.value = 0;
}

/* ===== 播报控制 ===== */
function stopTTS() {
  ttsBus.emit("tts:stop");
  ttsPlay.value = false;
  ttsText.value = "";
}

const isAudioing = ref(true);
function toggleAudio() {
  isAudioing.value = !isAudioing.value;
  if (!isAudioing.value) stopTTS();
}

watch(ttsPlay, (v) => {
  if (!isAudioing.value && v) stopTTS();
});
</script>


<style scoped>
/* ===== Root layout ===== */
.page-root {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* ===== Common utilities ===== */
.cover-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.text-strong { font-weight: 600; }

.icon-xxl { width: 2.4vw; height: 2.4vw; }
.icon-sm  { width: 2.6vh; height: 2.6vh; }
.icon-md  { width: 2.8vh; height: 2.8vh; }
.icon-xs  { width: 2.2vh; height: 2.2vh; }

.icon-strong { color: #111827; }
.icon-dim    { color: #4b5563; }

/* ===== Top area ===== */
.top-area {
  position: relative;
  width: 100%;
  height: 34.9vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all .3s ease;
}
.topbar {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  padding: 3vh 3vw 0 3vw; /* pt-[3vh] p-[3vw] */
}
.logo { height: 8vh; width: 8vh; }
.patient-info { flex: 1; margin-left: 3vw; }
.patient-row {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-evenly;
  font-size: 2vw;
  font-weight: 500;
  color: #374151; /* text-gray-700 */
}
.patient-item {
  display: flex;
  align-items: center;
  gap: 1vw;
}

/* ===== Process area ===== */
.process-area {
  position: absolute;
  top: 13vh;
  width: 100%;
  height: 14.6vh;
  z-index: 10;
  padding-left: 3.4vw;
  padding-right: 3.4vw;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  background: linear-gradient(to bottom, rgba(249, 251, 255, 0.5), rgba(249, 251, 255, 0));
}
.process-inner { width: 100%; height: 100%; position: relative; }
.process-row {
  position: absolute;
  top: 2vh;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1.6vw;
}
.process-title {
  flex-shrink: 0;
  min-width: 160px;
  font-size: 2.4vh;
  color: #1f2937; /* gray-800 */
}
.process-current { font-weight: 700; color: #111827; }
.process-total { font-size: 1.2vw; color: #6b7280; }

.progress { width: 100%; }
.progress-track {
  width: 100%;
  height: 1.4vw;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(1px);
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 9999px;
  background: linear-gradient(90deg, #8B81FF, #8891f7, #62C3FC);
  box-shadow: 0 1px 4px rgba(86, 167, 255, 0.45);
  transition: width .25s ease;
}

/* ===== Main area ===== */
.main-area {
  position: absolute;
  top: 20.4vh;
  z-index: 20;
  width: 100%;
  height: 79.6vh;
  display: flex;
  padding-top: 4px;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  background: linear-gradient(135deg, #F2F2F5, #E9EDF7);
}

/* Doctor column */
.doctor-area {
  width: 27.5vw;
  padding-left: 16px;
  padding-top: 8vh;
  position: relative;
}
.doctor-img {
  object-fit: contain;
  user-select: none;
  pointer-events: none;
}

/* Decorative overlay already in <style> below for #doctorpic-area::after */

/* QA column */
.qa-area {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  align-items: center;
  padding-top: 1.6vh;
  padding-right: 2vw;
}
.chat-area {
  width: 100%;
  height: 60vh;
  overflow-y: auto;
  padding-right: 1vw;
}

/* Message line */
.msg-block { width: 100%; margin: 4px 0; }
.msg-line { width: 100%; display: flex; }
.align-start { justify-content: flex-start; }
.align-end   { justify-content: flex-end; }

.msg-bundle {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  max-width: 50vw;
}
.msg-bundle.reverse { flex-direction: row-reverse; }
.avatar { box-shadow: 0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -4px rgba(0,0,0,.1); }
.avatar { flex-shrink: 0; }  /* 简写版本，也能解决被挤压 */

/* Bubble */
.bubble {
  position: relative;
  white-space: pre-wrap;
  word-break: break-word;
  vertical-align: top;
  padding: 12px 20px;
  margin: 12px 0;
  box-shadow: 0 0 12px rgba(0,0,0,0.10);
  border-radius: 12px;
  flex: 1 1 auto;      /* 关键：让气泡承担伸缩 */
  min-width: 0;        /* 关键：允许内容内部换行而不是撑破布局 */
  white-space: pre-wrap;
  word-break: break-word;
}
.bubble-assistant {
  background: #fff;
  color: #111827;
  border-top-left-radius: 0;
}
.bubble-user {
  background: linear-gradient(-73deg, #62C3FC 0%, #8B81FF 100%);
  color: #fff;
  border-top-right-radius: 0;
}
.bubble-text-lg { font-size: 2.8vh; }
.bubble-text-md { font-size: 2.0vh; margin-top: 4px; }
.btn-link {
  margin-right: 0;
  margin-top: 8px;
  font-size: 2vh;
  color: #2563eb;
  background: transparent;
  border: 0;
  cursor: pointer;
  transition: opacity .2s ease;
}
.btn-link:hover { text-decoration: underline; }

/* Suggestion / options lines */
.btnline { width: 100%; display: flex; margin: 8px 0; }
.btnline-left  { justify-content: flex-start; }
.btnline-right { justify-content: flex-end; }
.btnline-wrap { display: flex; align-items: center; gap: 12px; max-width: 70vw; }
.btnline-wrap-left  { margin-left: 4.8rem; }
.btnline-wrap-right { margin-right: 4.8rem; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }

/* Chip button */
.chip-btn {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 5vh;
  background: #fff;
  border-radius: 10px;
  color: #1f2937;
  font-size: 2.2vh;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  transition: box-shadow .2s ease, transform .2s ease;
  border: 0;
  cursor: pointer;
}
.chip-btn:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.10); }

/* Chat control (bottom) */
.chat-control {
  position: relative;
  width: 100%;
  margin-top: 16px;
  padding: 0 2vw 2vh 2vw;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  gap: 1.6vw;
  user-select: none;
}

/* Prev/Next buttons */
.nav-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 2.2vw;
  height: 7.4vh;
  border-radius: 16px;
  background: #fff;
  color: #1f2937;
  font-size: 2.4vh;
  border: 0;
  cursor: pointer;
  transition: box-shadow .2s ease, transform .2s ease, opacity .2s ease;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.nav-btn:hover { box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
.nav-btn:disabled { opacity: .5; cursor: not-allowed; }

/* Center control bar */
.center-control {
  flex: 1 1 auto;
  overflow: hidden;
  display: flex;
  padding: 0 1.4vw;
  transition: all .2s ease;
  align-items: center;
  height: 7.4vh;
}
.center-control-boxed {
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.center-hint {
  flex: 1 1 auto;
  text-align: center;
  font-size: 2.6vh;
  color: #374151;
  cursor: pointer;
}

/* Icon button */
.icon-btn {
  margin-left: 12px;
  padding: 1.2vh;
  border-radius: 9999px;
  border: 0;
  background: transparent;
  cursor: pointer;
  transition: background-color .2s ease;
}
.icon-btn:hover { background: #f3f4f6; }

/* Text input + send */
.text-input {
  flex: 1 1 auto;
  height: 100%;
  outline: none;
  background: transparent;
  font-size: 2.6vh;
  padding: 0 0.6vw;
  color: #111827;
  border: 0;
}
.center-actions { display: flex; align-items: center; gap: 8px; }
.send-btn {
  margin-left: 4px;
  padding: 0 1.6vw;
  height: 5.6vh;
  border-radius: 12px;
  background: linear-gradient(-73deg, #62C3FC 0%, #8B81FF 100%);
  color: #fff;
  font-size: 2.2vh;
  box-shadow: 0 4px 12px rgba(98, 195, 252, 0.45);
  border: 0;
  cursor: pointer;
  transition: filter .2s ease;
}
.send-btn:hover { filter: brightness(1.05); }
.send-btn-inner { display: flex; align-items: center; gap: 8px; }

/* Recording mode */
.recording-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.2vw;
}
.control-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 1.4vw;
  height: 6.4vh;
  border-radius: 12px;
  background: #fff;
  color: #1f2937;
  font-size: 2.2vh;
  border: 0;
  cursor: pointer;
  transition: box-shadow .2s ease;
  box-shadow: 0 0 12px rgba(0,0,0,0.10);
}
.control-btn:hover { box-shadow: 0 0 14px rgba(0,0,0,0.12); }
.recording-center { flex: 1 1 auto; display: flex; flex-direction: column; align-items: center; }
.recording-timer {
  position: absolute;
  top: -5vh;
  margin-bottom: 0.8vh;
}
.timer-strong { color: #6C82FF; font-size: 2.4vh; font-weight: 600; }
.timer-dim { color: #6b7280; font-size: 2.2vh; }

.wave-box {
  width: 100%;
  height: 6.4vh; /* 约 60-70px */
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0,0,0,0.10);
  background: linear-gradient(-73deg, #62C3FC 0%, #8B81FF 100%);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 核心修改 1: 让内部的条垂直居中 */
.wave-bars { 
  display: flex; 
  align-items: center;  /* 原代码是 flex-end，改为 center */
  gap: 6px; 
  height: 3.6vh; 
}

/* 竖条波形动画 */
@keyframes wavePulse {
  0%   { transform: scaleY(0.4); opacity: 0.8; }
  50%  { transform: scaleY(1);   opacity: 1; }
  100% { transform: scaleY(0.4); opacity: 0.8; }
}

.wave-bar {
  display: inline-block;
  width: 0.5vw;
  /* 基础高度可以稍微统一，靠 animation 拉伸，或者保留原本的高度差异 */
  height: 2.4vh; 
  margin: 0;
  
  /* 核心修改 2: 改为全圆角 */
  border-radius: 10px; /* 原代码是 3px 3px 0px 0px */
  
  background: #fff;
  
  /* 核心修改 3: 动画从中心扩散 */
  transform-origin: center; /* 原代码是 center bottom */
  
  animation: wavePulse 1s ease-in-out infinite;
}

/* 为了让波形看起来更像图片中的随机/对称感，
  这里稍微调整了不同位置条的高度和延迟 
*/
.wave-bar:nth-child(4n + 1) { height: 8px;   animation-delay: 0ms; }
.wave-bar:nth-child(4n + 2) { height: 16px;  animation-delay: 120ms; }
.wave-bar:nth-child(4n + 3) { height: 3.2vh; animation-delay: 240ms; }
.wave-bar:nth-child(4n + 4) { height: 3.6vh;  animation-delay: 360ms; }

/* Scrollbar */
#chat-area::-webkit-scrollbar { width: 10px; }
#chat-area::-webkit-scrollbar-thumb { background: rgba(0, 0, 0, 0.12); border-radius: 8px; }

/* doctor overlay */
#doctorpic-area::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: linear-gradient(180deg, rgba(255, 255, 255, 0) 55%, #e9edf7 100%);
  pointer-events: none;
}

/* pop transitions (kept same names) */
.pop-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
  filter: blur(2px);
}
.pop-enter-active {
  transition: opacity .28s ease, transform .34s cubic-bezier(.2,.8,.2,1), filter .28s ease;
  transition-delay: calc(var(--i) * 80ms);
}
.pop-enter-to {
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0);
}
.pop-move { transition: transform .3s ease; }

/* ===== 顶部喇叭按钮（病人信息右侧） ===== */
.speaker-btn {
  flex: 0 0 auto;
  width: 4.2vh;
  height: 4.2vh;
  margin-left: 1.2vw;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  backdrop-filter: blur(2px);
  cursor: pointer;
  transition: all 0.2s ease;
}
.speaker-btn:hover {
  background: rgba(255,255,255,0.55);
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}
.speaker-ic {
  width: 2.2vh;
  height: 2.2vh;
  color: #1f2937;
  opacity: 0.95;
}

</style>
