// frontend/src/composables/useAudioRecorder.ts
import { ref, reactive, type Ref } from "vue";
import MicRecorder from "mic-recorder-to-mp3";

interface AudioItem {
    fileName: string;
    data: string;
    time: string;
}

export function useAudioRecorder(opts: {
    isApp: Ref<boolean>;
    onSTT: (text: string) => void; // STT 回调
}) {
    const { isApp, onSTT } = opts;

    const isRecording = ref(false);
    const audioFiles = reactive<AudioItem[]>([]);
    const Mp3 = new MicRecorder({ bitRate: 128, encoderSampleRate: 44100 });

    function dataURLtoBlob(dataURL: string): Blob {
        const [header, b64] = dataURL.split(",");
        const mime = header.match(/:(.*?);/)?.[1] || "application/octet-stream";
        const bin = atob(b64);
        const u8 = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
        return new Blob([u8], { type: mime });
    }

    async function uploadAudioFile(item: AudioItem) {
        const blob = dataURLtoBlob(item.data);
        const fd = new FormData();
        fd.append("file", blob, item.fileName);
        try {
        const resp = await fetch("/api/v1/file/uploadfile", {
            method: "POST",
            body: fd,
        });
        if (!resp.ok) throw new Error();
        const { file_url, filename } = await resp.json();
        await fetchSTTResult(file_url || filename);
        } catch {
        /* 静默失败以避免打断输入体验 */
        }
    }

    async function fetchSTTResult(fileUrl: string) {
        try {
        const resp = await fetch(
            `/api/v1/audio/stt?file_url=${encodeURIComponent(fileUrl)}`,
            { method: "POST", headers: { accept: "application/json" } }
        );
        if (!resp.ok) throw new Error();
        const result = await resp.json();
        const text = result.transcription || result.result || "";
        onSTT(text);
        } catch {
        /* 静默失败 */
        }
    }

    function startRecording() {
        if (isRecording.value) return;
        isRecording.value = true;
        if (isApp.value) {

            // 交由原生容器处理
            //@ts-ignore
            window.uni?.postMessage?.({ data: [{ type: "startRecording" }] });
        } else {

            Mp3.start().catch(() => {
                isRecording.value = false;
            });
        }
    }

    function stopRecording({ cancel = false } = {}) {
        if (!isRecording.value) return;
        isRecording.value = false;

        if (cancel) {
            if (!isApp.value) Mp3.stop();
            return;
        }

        if (isApp.value) {
            //@ts-ignore
            window.uni?.postMessage?.({ data: [{ type: "stopRecording" }] });
        } else {
            Mp3.stop()
                .getMp3()
                //@ts-ignore
                .then(([_, blob]) => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const data = reader.result as string;
                    const item = {
                    fileName: `rec-${Date.now()}.mp3`,
                    data,
                    time: new Date().toLocaleString(),
                    };
                    audioFiles.push(item);
                    uploadAudioFile(item);
                };
                reader.readAsDataURL(blob);
                })
                .catch(() => {});
        }
    }

    /** App 端回传录音数据时调用 */
    function handleReceiveAudio(audioData: { fileName: string; data: string }) {
        const item = {
            fileName: audioData.fileName,
            data: audioData.data,
            time: new Date().toLocaleString(),
        };
        audioFiles.push(item);
        uploadAudioFile(item);
    }

    return {
        isRecording,
        audioFiles,
        startRecording,
        stopRecording,
        handleReceiveAudio,
    };
}
