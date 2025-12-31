<!-- frontend/src/components/ChatInput.vue -->
<script setup lang="ts">
import { ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Textarea } from './ui/textarea'
import ActionIcon from '@/components/ActionIcon.vue'
import {
  Mic, MicOff, Send, VolumeXIcon, AudioWaveformIcon
} from 'lucide-vue-next'

/* ---------- Props & Emits ---------- */
const props = defineProps({
  modelValue : { type: String, default: '' },
  placeholder: { type: String, default: '请输入消息…' },
  isRecording: { type: Boolean, default: false },
  isAudioing: { type: Boolean, default: true },
})
const emit = defineEmits([
  'update:modelValue',
  'send',
  'audio-click',
  'mic-press-start',
  'mic-press-end'
])

/* ---------- 输入框双向绑定 ---------- */
const innerValue = ref(props.modelValue)
watch(innerValue, v => emit('update:modelValue', v))
watch(() => props.modelValue, v => { if (v !== innerValue.value) innerValue.value = v })

const commitSend = () => {
  if (!innerValue.value.trim()) return
  emit('send', innerValue.value.trim())
  innerValue.value = ''
}

/* ---------- 语音长按模式 ---------- */
const voicePressMode = ref(false)
const isPressing = ref(false)
let startPoint: DOMPoint | null = null
let longPressTimer: ReturnType<typeof setTimeout> | null = null

const LEAVE_RADIUS = 80
const PRESS_DELAY  = 500

function distance (e: PointerEvent) {
  if (!startPoint) return 0
  return Math.hypot(e.clientX - startPoint.x, e.clientY - startPoint.y)
}
function cleanupPress () {
  isPressing.value = false
  startPoint = null
  if (longPressTimer) { clearTimeout(longPressTimer); longPressTimer = null }
  window.removeEventListener('pointermove', onPressMove)
  window.removeEventListener('pointerup', onPressUp)
  window.removeEventListener('pointercancel', onPressCancel)
}
function onPressDown (e: PointerEvent) {
  if (!voicePressMode.value) return
  e.preventDefault()
  startPoint = new DOMPoint(e.clientX, e.clientY)
  isPressing.value = true
  longPressTimer = setTimeout(() => emit('mic-press-start'), PRESS_DELAY)
  window.addEventListener('pointermove', onPressMove, { passive: false })
  window.addEventListener('pointerup', onPressUp, { passive: false })
  window.addEventListener('pointercancel', onPressCancel, { passive: false })
}
function onPressMove () {}
function onPressUp (e: PointerEvent) {
  if (!isPressing.value) return
  cleanupPress()
  emit('mic-press-end', { cancel: distance(e) > LEAVE_RADIUS })
}
function onPressCancel () {
  if (!isPressing.value) return
  cleanupPress()
  emit('mic-press-end', { cancel: true })
}
function toggleVoiceMode () {
  voicePressMode.value = !voicePressMode.value
  if (voicePressMode.value)
    document.querySelector('#chat-textarea')?.blur()
}
// 录音状态外部变化：结束时确保把按压态和监听清掉
watch(() => props.isRecording, (now, prev) => {
  if (prev && !now) {
    // 录音结束：无论如何把局部按压态清理掉
    cleanupPress()
    // 若已有文本（通常是 STT 回填），自动退出语音模式，回到打字态（可按需保留）
    if (voicePressMode.value && innerValue.value.trim()) {
      voicePressMode.value = false
    }
  }
})

// 文本被回填（STT 写回来了）：如果当前不在录音中，自动退出语音模式
watch(() => props.modelValue, (v, old) => {
  if (v !== old && voicePressMode.value && !props.isRecording) {
    // 确认已不是录音态，再切回打字模式
    voicePressMode.value = false
  }
})
</script>

<template>
  <TooltipProvider>
    <div
      class="chat-input-container relative w-full flex flex-col gap-2 rounded-2xl border p-3 transition-all duration-300 overflow-hidden"
      :class="[
        voicePressMode
          ? 'bg-gradient-to-br from-[#eef6ff] to-[#e5f2ff] border-[#b4d4ff] ring-2 ring-[#4d98f3]'
          : 'bg-[#f8fcff] border-[#dfe7f0]',
        (isRecording && voicePressMode) && 'recording-active'
      ]"
      @pointerdown="onPressDown"
    >

      <!-- ===== 输入区 / 语音提示 ===== -->
      <div class="relative">
        <Textarea
          id="chat-textarea"
          v-model="innerValue"
          :readonly="voicePressMode"
          :tabindex="voicePressMode ? -1 : 0"
          :placeholder="voicePressMode
            ? '按住这一块开始说话 · 松开发送 · 上滑取消'
            : placeholder"
          rows="1"
          auto-grow
          class="resize-none border-none bg-transparent w-full
                 focus-visible:ring-0 focus-visible:ring-offset-0
                 placeholder:text-gray-400"
          @keyup.enter.prevent="!voicePressMode && commitSend()"
        />

        <!-- 语音模式覆盖层 -->
        <transition name="fade">
          <div
            v-if="voicePressMode"
            class="absolute inset-0 flex flex-col items-center justify-center
                   rounded-xl bg-white/40 backdrop-blur-sm pointer-events-none select-none"
          >
            <div
              class="text-[13px] text-gray-600 font-medium tracking-wide"
            >
              按住说话，松开发送，上滑取消
            </div>
          </div>
        </transition>
      </div>

      <!-- ===== 底部功能区 ===== -->
      <div class="flex items-center justify-between z-30">
        <!-- 左侧：语音播报 -->
        <div class="flex items-center gap-1">
          <ActionIcon label="语音播报" @click="$emit('audio-click')">
            <template #icon>
              <component :is="isAudioing ? AudioWaveformIcon : VolumeXIcon"
                         class="w-7 h-7" />
            </template>
          </ActionIcon>
        </div>

        <!-- 右侧：语音模式切换 + 发送 -->
        <div class="flex items-center gap-3 z-30">
          <ActionIcon
            :label="voicePressMode ? '退出语音长按模式' : '进入语音长按模式'"
            @click="toggleVoiceMode"
          >
            <template #icon>
              <component :is="voicePressMode ? MicOff : Mic"
                         class="w-6 h-6" />
            </template>
          </ActionIcon>

          <Button size="icon"
            @click="commitSend"
            class="bg-[#37bbf8] hover:bg-[#5dc2ff] text-white shadow-md transition-colors">
            <Send class="w-5 h-5" />
          </Button>
        </div>
      </div>

      <!-- ===== 录音动画层 ===== -->
      <transition name="fade">
        <div
          v-if="(isPressing && voicePressMode) || (isRecording && voicePressMode)"
          class="absolute inset-0 flex flex-col items-center justify-center
                bg-[#00000033] text-white text-sm rounded-2xl z-20"
        >
          <div class="recording-wave"></div>
          <div class="mt-3 font-semibold tracking-wide">正在录音… 松开发送</div>
        </div>
      </transition>
    </div>
  </TooltipProvider>
</template>

<style scoped>
.chat-input-container {
  box-shadow: 0 4px 8px rgba(0,0,0,0.04);
}

/* 波纹动画层 */
.recording-active::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 1rem;
  background: radial-gradient(circle at center,
    rgba(77,152,243,0.35) 0%, transparent 70%);
  animation: pulseGlow 1.5s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%,100% { opacity: 0.5; transform: scale(1); }
  50%     { opacity: 0.9; transform: scale(1.03); }
}

/* 录音波纹 */
.recording-wave {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255,255,255,0.25);
  position: relative;
  animation: wavePulse 1.2s infinite ease-in-out;
}
.recording-wave::after {
  content:'';
  position:absolute;
  inset:0;
  border-radius:50%;
  border:2px solid rgba(255,255,255,0.8);
  animation: waveRing 1.2s infinite ease-out;
}
@keyframes wavePulse {
  0%,100% { transform:scale(1); opacity:.8; }
  50% { transform:scale(1.1); opacity:1; }
}
@keyframes waveRing {
  0% { transform:scale(1); opacity:1; }
  100% { transform:scale(1.8); opacity:0; }
}

/* 淡入淡出 */
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
