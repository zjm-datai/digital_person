// frontend/src/composables/useAudioRecorder.ts
import { ref, reactive, type Ref } from "vue";
import MicRecorder from "mic-recorder-to-mp3";

interface AudioItem {
  fileName: string;
  data: string; // dataURL
  time: string;
}

export function useAudioRecorder(opts: {
  isApp: Ref<boolean>;
  onSTT: (text: string) => void;
  organizeCode: Ref<string>;
  conversationId?: Ref<string | null>;
}) {
  const { isApp, onSTT, organizeCode, conversationId } = opts;

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

  
  function dataURLtoAudioFile(item: AudioItem): File {
    const blob = dataURLtoBlob(item.data);

    // 后端只认 audio/mpeg 或 audio/wav
    let type = blob.type;

    // 常见不规范情况：audio/mp3 / application/octet-stream
    if (item.fileName.toLowerCase().endsWith(".mp3")) type = "audio/mpeg";
    if (item.fileName.toLowerCase().endsWith(".wav")) type = "audio/wav";

    return new File([blob], item.fileName, { type });
  }

  async function uploadAudioFile(item: AudioItem) {
    try {
      const file = dataURLtoAudioFile(item);

      const fd = new FormData();
      fd.append("file", file); // 字段名必须是 file
      fd.append("organize_code", organizeCode.value);

      const cid = conversationId?.value ?? null;
      
      console.log("conversation_id:", cid)
      
      if (cid) fd.append("conversation_id", cid);

      const resp = await fetch("/audio_api/audio/transcription", {
        method: "POST",
        body: fd,
        headers: {
          accept: "application/json",
        },
      });

      if (!resp.ok) throw new Error(await resp.text());

      const result = await resp.json();
      // 后端返回：{ transcription: string, file_id: string }
      onSTT(result.transcription || "");
    } catch {
      /* 静默失败以避免打断输入体验 */
    }
  }

  function startRecording() {
    if (isRecording.value) return;
    isRecording.value = true;

    if (isApp.value) {
      // 交由原生容器处理
      // @ts-ignore
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
      // @ts-ignore
      window.uni?.postMessage?.({ data: [{ type: "stopRecording" }] });
    } else {
      Mp3.stop()
        .getMp3()
        // @ts-ignore
        .then(([_, blob]) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const data = reader.result as string;
            const item: AudioItem = {
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
    const item: AudioItem = {
      fileName: audioData.fileName,
      data: audioData.data, // 这里假设是 dataURL；如果是纯 base64，见下面说明
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
