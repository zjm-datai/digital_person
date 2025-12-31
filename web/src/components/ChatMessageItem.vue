<!-- frontend/src/components/ChatMessageItem.vue -->

<template>
    <!-- 行容器：助手靠左，用户靠右；不使用 row-reverse，避免主轴语义变化 -->
    <div
        class="flex items-start gap-2 my-1 w-full"
        :class="isAssistant ? 'justify-start' : 'justify-end'"
    >
        <!-- 头像：使用 order 控制位置，确保“头像在该侧的开头” -->
        <el-avatar
            v-if="isAssistant || userAvatar"
            :src="isAssistant ? doctorAvatar : userAvatar"
            size="default"
            class="shrink-0 shadow-lg"
            :class="isAssistant ? 'order-1' : 'order-2'"
        />

        <!-- 气泡：同样用 order，用户气泡在头像的左侧（order-1） -->
        <div
            :class="[
                'relative rounded-2xl px-3 py-2 whitespace-pre-wrap break-words max-w-[72%]',
                isAssistant ? 'text-gray-800 order-2' : 'bg-[#37bbf8] text-white order-1 shadow-lg'
            ]"
        >
            <!-- 思考开关（仅助手消息且存在思考时显示） -->
            <button
                v-if="isAssistant && msg.thinking && toggleableThinking"
                class="thinking-toggle"
                type="button"
                :aria-pressed="isThinkingVisible ? 'true' : 'false'"
                :title="isThinkingVisible ? '隐藏思考' : '显示思考'"
                @click="isThinkingVisible = !isThinkingVisible"
            >
                {{ isThinkingVisible ? '隐藏思考' : '显示思考' }}
            </button>

            <!-- 思考块 -->
            <div
                v-if="isAssistant && msg.thinking && isThinkingVisible"
                class="thinking-text"
            >
                {{ msg.thinking }}
            </div>

            <!-- 普通可见内容（最小转义） -->
            <div v-html="formatVisible(msg.content)"></div>

            <div v-if="msg.suggestions?.length" class="flex flex-wrap gap-2 mt-6">
                <transition-group
                    name="pop"
                    tag="div"
                    appear
                    class="flex flex-wrap gap-2"
                    v-if="msg.suggestions?.length"
                >
                    <button
                        v-for="(s, i) in msg.suggestions"
                        :key="s + '-' + i"
                        class="px-3 py-1.5 text-xs rounded-sm shadow-lg bg-[#eef2ff]
                            border border-[#dbe2ff] cursor-pointer hover:bg-[#e6ebff]
                            transition-colors duration-200"
                        @click="onSuggestionClick(s)"
                        :style="{ '--i': i }"
                    >
                        {{ s }}
                    </button>
                </transition-group>

            </div>



            <div v-if="msg.summary" v-html="formatVisible(msg.summary)"></div>

            <button
                v-if="isAssistant && msg.summary"
                @click="handleSummaryClick"
                class="mr-0 mt-4 text-sm text-blue-600 hover:underline transition"
            >
                🌟 查看总结报告
            </button>

        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { ChatMessage } from "@/types/web/chat";

/**
 * Props
 * - userAvatar: 用户头像（可选）
 * - defaultShowThinking: 默认是否展示思考（默认 true）
 * - toggleableThinking : 是否显示“显示/隐藏思考”按钮（默认 true）
 */
const props = withDefaults(
    defineProps<{
        msg: ChatMessage;
        doctorAvatar: string;
        userAvatar?: string;
        defaultShowThinking?: boolean;
        toggleableThinking?: boolean;
    }>(),
    {
        defaultShowThinking: true,
        toggleableThinking: true,
    }
);

const emit = defineEmits<{
    (e: "suggestion-click", text: string): void;
}>();

function onSuggestionClick(text: string) {
    emit("suggestion-click", text);
}

const isAssistant = computed(() => props.msg.role === "assistant");

/** 每条消息独立的思考显示状态 */
const isThinkingVisible = ref<boolean>(props.defaultShowThinking);
watch(() => props.defaultShowThinking, v => (isThinkingVisible.value = v));

/** 最小转义，避免把尖括号当标签渲染 */
function formatVisible(raw: string): string {
    if (!raw) return "";
    return raw.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

import { useRouter } from "vue-router";
const router = useRouter();

function handleSummaryClick() {
    router.push("/report");
}


</script>

<style scoped>
/* 思考块：灰底虚线、简约易分辨 */
.thinking-text {
    display: block;
    width: 100%;
    white-space: pre-wrap;
    word-break: break-word;
    color: #666;
    background-color: #f7f7f8;
    border-left: 3px dashed #cfcfcf;
    padding: 8px 12px;
    margin: 2px 0 8px;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.5;
}

/* 思考开关按钮：小圆角，悬浮轻微变化；位置在气泡右上角 */
.thinking-toggle {
    position: absolute;
    top: 0px;
    right: -48px;
    font-size: 11px;
    line-height: 1;
    padding: 4px 6px;
    border: 1px solid #e5e7eb;
    border-radius: 9999px;
    background: #ffffff;
    color: #606266;
    cursor: pointer;
    opacity: .9;
}
.thinking-toggle:hover { opacity: 1; border-color: #d1d5db; }
.thinking-toggle:active { transform: translateY(1px); }

/* 别名和你上面的 scoped 并不冲突，保留即可 */
.pop-enter-from {
    opacity: 0;
    transform: translateY(8px) scale(0.96);
    filter: blur(2px);
}
.pop-enter-active {
    transition: opacity .28s ease, transform .34s cubic-bezier(.2,.8,.2,1), filter .28s ease;
    transition-delay: calc(var(--i) * 80ms); /* 核心：按索引阶梯延迟 */
}
.pop-enter-to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
}

/* 列表重新排序/新增时的位移动画（FLIP） */
.pop-move {
    transition: transform .3s ease;
}

/* 全局一键隐藏（父级容器加 .hide-thinking） */
:global(.hide-thinking) .thinking-text,
:global(.hide-thinking) .thinking-toggle { display: none !important; }
</style>
