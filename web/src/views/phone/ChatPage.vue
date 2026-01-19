<template>
  <div
    class="w-full h-screen py-[2vh] overflow-hidden bg-gradient-to-b from-[#f0effa] via-sky-50 to-white flex flex-col items-center"
  >
    <!-- 顶部区域 -->
    <div
      id="top-area"
      class="w-full max-w-5xl flex-shrink-0 flex flex-col px-[4vw]"
    >
      <!-- logo + 患者信息 -->
      <div class="flex items-center justify-between">
        <img src="@/assets/logo@2x.png" alt="logo" class="h-[9vw] w-[10vw]" />
        <div
          id="patient-info"
          class="flex-1 flex items-center justify-evenly ml-1 text-[4vw] font-semibold text-gray-600"
        >
          <div class="flex items-center gap-1">
            <img src="@/assets/user.svg" alt="patient-icon" class="w-[3.8vw] h-[2vh]" />
            <span>{{ patient.name }}</span>
          </div>
          <div class="flex items-center gap-1">
            <img src="@/assets/keshi.svg" alt="patient-icon" class="w-[3.8vw] h-[2vh]" />
            <span>{{ patient.age }} 岁</span>
          </div>
          <div class="flex items-center gap-1">
            <img src="@/assets/keshi_2.svg" alt="patient-icon" class="w-[3.8vw] h-[2vh]" />
            <span>{{ patient.department }}</span>
          </div>
        </div>
      </div>

      <!-- 顶部提示文案 -->
      <div
        class="mt-[2.2vh] p-2 bg-white/90 rounded-lg text-[4vw] font-medium text-gray-600"
      >
        为方便医生全面了解病情、提供更好诊疗，麻烦您如实回答以下问题，感谢配合！
      </div>

      <!-- 进度条 -->
      <div class="mt-[0.8vh] space-y-2">
        <div class="flex items-center justify-between text-[4vw] font-semibold text-gray-600">
          <div class="flex items-center justify-center gap-6">
            <span>答题进度</span>
            <div>
              <span class="text-blue-400 text-[5vw]">{{ current }}</span>
              <span class="font-medium text-gray-400">/{{ total }}</span>
            </div>
          </div>
          <button
              class=""
              @click="toggleAudio"
            >
              <component :is="isAudioing ? VolumeXIcon : AudioWaveformIcon" class="w-5 h-5" />
          </button>
        </div>

        <div class="w-full h-[1vh] rounded-full bg-blue-100 overflow-hidden">
          <div
            class="h-full rounded-full bg-gradient-to-r from-[#8B81FF] via-[#8891f7] to-[#62C3FC] transition-all"
            :style="{ width: percent + '%' }"
          />
        </div>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div
      id="chat-area"
      class="w-full mt-[2.4vh] flex-1 min-h-0 overflow-y-auto px-[4vw]"
    >
      <div v-for="(msg, idx) in qaWindow" :key="`qa-${idx}`" class="w-full mt-0 mb-6">
        <!-- 气泡 -->
        <div
          class="w-full flex"
          :class="msg.role === 'assistant' ? 'justify-start' : 'justify-end'"
        >
          <div
            class="flex items-start gap-[2.5vw] max-w-[80%]"
            :class="msg.role === 'assistant' ? '' : 'flex-row-reverse'"
          >
            <img
              :src="msg.role === 'assistant' ? doctorAvatar : userAvatar"
              class="w-[8.6vw] h-[8.6vw] rounded-full object-cover shrink-0 shadow-lg"
              alt="avatar"
            />

            <div
              :class="[
                'relative whitespace-pre-wrap break-words align-top p-[2.2vw] mb-1 shadow-[0_0_12px_rgba(0,0,0,0.10)]',
                msg.role === 'assistant'
                  ? 'bg-white text-gray-900 rounded-tr-[8px] rounded-br-[8px] rounded-bl-[8px] rounded-tl-[0px]'
                  : 'bg-[linear-gradient(-73deg,_#62C3FC_0%,_#8B81FF_100%)] text-white rounded-tl-[8px] rounded-tr-[0px] rounded-br-[8px] rounded-bl-[8px]'
              ]"
            >
              <div class="text-[4vw]">{{ msg.content }}</div>
              <div v-if="msg.summary" class="text-[3.2vw] mt-1">
                {{ msg.summary }}
              </div>

              <button
                v-if="msg.role === 'assistant' && msg.summary"
                @click="handleSummaryClick"
                class="mr-0 mt-[1vh] text-[3.2vw] text-blue-600 hover:underline transition"
              >
                🌟 查看总结报告
              </button>
            </div>
          </div>
        </div>

        <!-- 外置按钮行 -->
        <transition-group name="pop" tag="div" appear>
          <!-- 推荐答案 -->
          <div
            v-if="msg.role === 'assistant' && isLatestRound && dedupeArray(msg.suggestions || []).length"
            class="w-full flex my-1 justify-start"
          >
            <div class="flex items-center gap-1 max-w-[80%] ml-[12vw]">
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="(s, i) in dedupeArray(msg.suggestions || [])"
                  :key="`sug-${idx}-${i}`"
                  class="px-2 py-1 h-[4vh] bg-white rounded-[1vh] 
                  text-gray-600 text-[3.2vw] shadow-[0_2px_10px_rgba(0,0,0,0.08)] 
                  hover:shadow-[0_4px_12px_rgba(0,0,0,0.10)] transition"
                  @click="onSuggestionClick(s)"
                >
                  {{ s }}
                </button>
              </div>
            </div>
          </div>

          <!-- 接近选项 -->
          <div
            v-if="msg.role === 'user' && isLatestRound && isAnchor(msg)"
            class="w-full flex my-2 justify-end"
          >
            <div class="flex items-center gap-1 max-w-[80%] mr-[1vw]">
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="(opt, i) in nearestOptions"
                  :key="`near-${idx}-${i}`"
                  class="px-2 h-[4vh] bg-white rounded-[1vw] text-gray-800 text-[3.2vw] shadow-[0_2px_10px_rgba(0,0,0,0.08)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.10)] transition"
                  @click="onPickNearest(opt)"
                >
                  {{ opt.label }}
                </button>

                <button
                  class="px-2 h-[4vh] bg-white rounded-[10px] text-gray-800 text-[3.2vw] shadow-[0_2px_10px_rgba(0,0,0,0.08)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.10)] transition"
                  @click="onRetryInput"
                >
                  重新输入
                </button>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
    </div>

    <!-- 底部输入 + 控制区 -->
    <div id="control-area" class="w-full mt-2 px-4 pb-[1vh] flex-shrink-0">
      <!-- 上一题 / 下一题 & 录音提示 -->
      <!-- 未录音：显示上一题/下一题 -->
      <div v-if="!isRecording" class="flex gap-4 mb-2">
        <button
          class="flex-1 h-[6vh] rounded-[14px] bg-white text-gray-800 text-[4vw] shadow-[0_4px_16px_rgba(0,0,0,0.06)] 
          flex items-center justify-center gap-2"
          @click="handlePrev"
        >
          <ChevronLeft class="w-4 h-4" /> 上一题
        </button>
        <button
          class="flex-1 h-[6vh] rounded-[14px] bg-white text-gray-800 text-[4vw] shadow-[0_4px_16px_rgba(0,0,0,0.06)] 
          flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          @click="handleNext"
          :disabled="isLatestRound && !hasUserInCurrentRound"
        >
          下一题 <ChevronRight class="w-4 h-4" />
        </button>
      </div>

      <!-- 录音中：上一题/下一题位置改成提示文案 -->
      <div
        v-else
        class="mb-4 h-[6vh] rounded-[14px] text-[4vw] text-gray-700
              flex items-center justify-center"
      >
        正在录音，
        <span class="mx-1 text-blue-600 font-semibold">{{ remainSeconds }}s</span>
        后停止录音
      </div>

      <!-- 输入区域 -->
      <div
        :class="[
          'w-full rounded-[16px] bg-white',
          isRecording ? 'px-4' : 'h-[6vh] px-4 flex items-center  shadow-[0_4px_16px_rgba(0,0,0,0.06)]'
        ]"
      >
        <!-- 默认语音入口 -->
        <template v-if="!isTypingMode && !isRecording">
          <div
            class="flex-1 text-center text-[4vw] text-gray-700 cursor-pointer"
            @click="startRecordingUI"
          >
            点击进入语音识别
          </div>
          <button
            class="ml-3 p-2 rounded-full hover:bg-gray-100 transition"
            @click="
              isTypingMode = true;
              $nextTick(() => inputRef?.focus())
            "
          >
            <Keyboard class="w-[6vw] h-[6vw] text-gray-700" />
          </button>
        </template>

        <!-- 文本输入 -->
        <template v-else-if="isTypingMode">
          <input
            ref="inputRef"
            v-model="inputValue"
            type="text"
            placeholder="请输入内容..."
            class="flex-1 h-full outline-none bg-transparent text-[3.6vw] px-2 text-gray-900"
            @keydown.enter.prevent="sendInput"
          />
          <div class="flex items-center gap-2">
            <button
              class="p-2 rounded-full hover:bg-gray-100 transition"
              @click="isTypingMode = false"
              title="返回语音模式"
            >
              <Mic class="w-[4vw] h-[4vw] text-gray-700" />
            </button>
            <button
              class="ml-1 px-4 h-[3.6vh] rounded-[12px] bg-[linear-gradient(-73deg,#62C3FC_0%,#8B81FF_100%)] text-white text-[4vw] shadow-[0_4px_12px_rgba(98,195,252,0.45)] hover:brightness-105 transition flex items-center justify-center"
              @click="sendInput"
            >
              <Send class="w-[4vw] h-[4vw]" />
            </button>
          </div>
        </template>

        <!-- 录音模式：只有波浪块 + 结束录音按钮 -->
        <template v-else>
          <div class="w-full flex items-center justify-between gap-3 h-[6vh]">
            <!-- 波形背景 -->
            <div
              class="flex-1 min-w-0 h-full rounded-[1vh] bg-gradient-to-r from-blue-400 to-purple-500
                    shadow-[0_0_12px_rgba(0,0,0,0.1)] px-4 flex items-center justify-center overflow-hidden"
            >
              <div class="flex items-end justify-between h-[3.6vh] w-full">
                <span v-for="i in 24" :key="i" class="wave-bar" />
              </div>
            </div>

            <!-- 结束按钮 -->
            <button
              class="shrink-0 flex items-center gap-2 px-6 h-full rounded-[12px] bg-white text-gray-800 text-[3.6vw]
                    shadow-[0_0_12px_rgba(0,0,0,0.1)] hover:shadow-[0_0_14px_rgba(0,0,0,0.12)] transition-all"
              @click="endRecordingUI"
            >
              <span>结束录音</span>
              <Send class="w-[4vw] h-[4vw]" />
            </button>
          </div>
        </template>

      </div>
    </div>

    <WebsocketTTS />

  </div>
</template>

<style scoped>
/* 滚动条 */
#chat-area::-webkit-scrollbar {
  width: 10px;
}
#chat-area::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}

/* 波形动画 */
@keyframes wavePulse {
  0% { transform: scaleY(0.3); opacity: 0.9; }
  50% { transform: scaleY(1); opacity: 1; }
  100% { transform: scaleY(0.3); opacity: 0.9; }
}
.wave-bar {
  display: inline-block;
  flex: 0 0 3px;   /* 每个条子 3px 左右 */
  height: 1.2vh;
  margin: 0 1px;
  border-radius: 999px;
  background: white;
  transform-origin: center bottom;
  animation: wavePulse 900ms ease-in-out infinite;
}
.wave-bar:nth-child(4n + 1) { height: 8px; animation-delay: 0ms; }
.wave-bar:nth-child(4n + 2) { height: 12px; animation-delay: 120ms; }
.wave-bar:nth-child(4n + 3) { height: 16px; animation-delay: 240ms; }
.wave-bar:nth-child(4n + 4) { height: 20px; animation-delay: 360ms; }

/* 动画 */
.pop-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
  filter: blur(2px);
}
.pop-enter-active {
  transition: opacity 0.28s ease, transform 0.34s cubic-bezier(0.2, 0.8, 0.2, 1), filter 0.28s ease;
}
.pop-enter-to {
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0);
}
.pop-move {
  transition: transform 0.3s ease;
}
</style>

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
  },

  organizeCode: computed(() => patientStore.scanCode || "zhonyiyuan"),

  conversationId: sid,
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
  console.log("sid.value:", sid.value)
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
    const url = new URL("/console_api/asr/suggest", window.location.origin);
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
