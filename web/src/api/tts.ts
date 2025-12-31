// frontend/src/api/tts.ts

import { ref } from "vue";
// import { ElNotification } from "element-plus";

// 配置接口结构
export interface TTSConfig {
    url: string;
    headers: Record<string, string>;
    model: string;
    voice: string;
}

const DEFAULT_TTS_CONFIG: TTSConfig = {
    url: "/api/v1/tts",
    headers: {
        "Content-Type": "application/json",
    },
    model: "", // 后端已固定，可留空
    voice: "FunAudioLLM/CosyVoice2-0.5B:anna",
};

const audioInstance = ref<HTMLAudioElement | null>(null);
export const isPlaying = ref<boolean>(false);
let streamAbortController: AbortController | null = null;

// 通用通知提示
// const showNotification = (
//     message: string,
//     type: "success" | "info" | "warning" | "error" = "info"
// ) => {
//     ElNotification({
//         title: "TTS 语音合成",
//         message,
//         type,
//         position: "top-right",
//         duration: 3000,
//     });
// };


// 停止播放并清理资源
export const stopAudio = () => {
    if (audioInstance.value) {
        audioInstance.value.pause();
        if (audioInstance.value.src) {
            URL.revokeObjectURL(audioInstance.value.src);
        }
        audioInstance.value = null;
    }
    isPlaying.value = false;

    if (streamAbortController) {
        streamAbortController.abort();
        streamAbortController = null;
    }
};

// 播放音频 blob
const playAudio = (blob: Blob) => {
    stopAudio();
    console.log("blob.type:", blob.type)
    const audioUrl = URL.createObjectURL(blob);
    const audio = new Audio(audioUrl);
    audioInstance.value = audio;

    audio.onplay = () => {
        isPlaying.value = true;
    };

    audio.onpause = () => {
        isPlaying.value = false;
    };

    audio.onended = () => {
        stopAudio();
    };

    audio.play().catch((error) => {
        // showNotification("音频播放失败，请检查浏览器权限", "warning");
        console.error("Audio play error:", error);
        stopAudio();
    });
};

// 主方法：请求语音并播放
export const textToSpeech = async (
    text: string,
    customConfig?: Partial<TTSConfig>
): Promise<string | null> => {
    const trimmedText = text.trim();
    if (!trimmedText) {
        // showNotification("没有可转换的文本内容", "info");
        return null;
    }

    const ttsConfig: TTSConfig = {
        ...DEFAULT_TTS_CONFIG,
        ...customConfig,
        headers: {
            ...DEFAULT_TTS_CONFIG.headers,
            ...customConfig?.headers,
        },
    };

    try {
        // showNotification("正在合成语音...", "info");

        const response = await fetch(ttsConfig.url, {
            method: "POST",
            headers: ttsConfig.headers,
            body: JSON.stringify({
                text: trimmedText,
                voice: ttsConfig.voice,
                stream: true,
            }),
        });

        if (!response.ok) {
            throw new Error(`TTS请求失败: ${response.status} ${response.statusText}`);
        }

        const audioBlob = await response.blob();
        // showNotification("语音合成成功", "success");

        playAudio(audioBlob);
        return URL.createObjectURL(audioBlob); // 可用于外部用途
    } catch (error: any) {
        // showNotification(`语音合成失败: ${error.message}`, "error");
        console.error("TTS error:", error);
        return null;
    }
};

// 清理播放状态
export const cleanupTTS = () => {
    stopAudio();
};

// 导出
export default {
    textToSpeech,
    stopAudio,
    isPlaying,
    cleanupTTS,
};
