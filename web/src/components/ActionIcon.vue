<!-- frontend/src/components/ActionIcon.vue -->

<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import {
    Tooltip,
    TooltipTrigger,
    TooltipContent,
} from '@/components/ui/tooltip'

/* ------- 接收 Props / Emits ------- */
defineProps<{ label: string }>()
const emit = defineEmits<{
    (e: 'click'): void
    (e: 'record-start'): void
    (e: 'record-end'): void
    (e: 'record-cancel'): void
}>()

const isPressing = ref(false)
let startPoint: DOMPoint | null = null
let longPressTimer: ReturnType<typeof setTimeout> | null = null

function distance (e: PointerEvent) {
    if (!startPoint) return 0
    return Math.hypot(e.clientX - startPoint.x, e.clientY - startPoint.y)
}
const LEAVE_RADIUS = 80               // 滑出 80px 视为取消
const PRESS_DELAY  = 500              // 长按 0.5 秒才触发录音
function onPointerDown (e: PointerEvent) {

    e.preventDefault()

    startPoint  = new DOMPoint(e.clientX, e.clientY)
    isPressing.value = true
    longPressTimer = setTimeout(() => emit('record-start'), PRESS_DELAY)

    window.addEventListener('pointermove', onPointerMove, { passive: false })
    window.addEventListener('pointerup', onPointerUp, { passive: false })
    window.addEventListener('pointercancel', onPointerCancel, { passive: false })
}

function onPointerMove (e: PointerEvent) {
    if (!isPressing.value) return
    // 手指滑出太远，提示可能取消（可选：加 UI）
    if (distance(e) > LEAVE_RADIUS) {
        // 这里不 emit cancel，等松手时统一判定
    }
}

function onPointerUp (e: PointerEvent) {
    if (!isPressing.value) return
    cleanup()

    const cancelled = distance(e) > LEAVE_RADIUS
    // @ts-ignore
    emit(cancelled ? 'record-cancel' : 'record-end')
}

function onPointerCancel () {
    if (!isPressing.value) return
    cleanup()
    emit('record-cancel')
}

function cleanup () {
    isPressing.value = false
    startPoint = null
    if (longPressTimer) { clearTimeout(longPressTimer); longPressTimer = null }
    window.removeEventListener('pointermove', onPointerMove)
    window.removeEventListener('pointerup', onPointerUp)
    window.removeEventListener('pointercancel', onPointerCancel)
}
</script>

<template>
    <Tooltip>
        <TooltipTrigger as-child>
        <Button
            variant="ghost"
            size="icon"
            class="select-none text-muted-foreground"
            @pointerdown="onPointerDown"
            @click="$emit('click')"
        >
            <!-- 这里渲染父组件传入的 <template #icon> -->
            <slot name="icon" />
        </Button>
        </TooltipTrigger>

        <TooltipContent>{{ label }}</TooltipContent>
    </Tooltip>
</template>

<style scoped>
button {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    user-select: none;
}
</style>