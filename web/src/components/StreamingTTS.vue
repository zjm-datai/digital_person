<template>
    <!-- 隐藏的 audio 元素 -->
    <audio ref="audioEl" hidden></audio>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue';

interface Props {
  /** 要合成并播放的文本 */
  text: string;
  /** true 时开始继续播放，false 时停止并清理 */
  play: boolean;
}
const props = defineProps<Props>();

// —— 按你的部署环境调整 —— //
const TTS_URL = 'http://211.90.240.240:30055/v1/audio/speech';

let mediaSource: MediaSource | null      = null;
let sourceBuffer: SourceBuffer | null    = null;
let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
let fetchController: AbortController | null = null;
let queue: Uint8Array[] = [];
let readingDone = false;

const audioEl = ref<HTMLAudioElement>();

async function startStreaming() {
  cleanup();

  fetchController = new AbortController();

  const res = await fetch(TTS_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input: props.text,
      voice: 'doctor_woman',
      speed: 1.0,
      stream: true,
      response_format: 'mp3',
      sample_rate: 24000, // 可根据需要调整/删除
    }),
    signal: fetchController.signal,
  });

  if (!res.ok || !res.body) {
    console.error('TTS 流式接口错误:', res.status);
    return;
  }

  mediaSource = new MediaSource();
  audioEl.value!.src = URL.createObjectURL(mediaSource);

  mediaSource.addEventListener('sourceopen', () => {
    if (!mediaSource) return;
    sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
    sourceBuffer.mode = 'sequence';
    reader = res.body!.getReader();
    readingDone = false;
    queue = [];

    sourceBuffer.addEventListener('updateend', () => {
      if (queue.length > 0 && sourceBuffer && !sourceBuffer.updating) {
        sourceBuffer.appendBuffer(queue.shift()!);
      } else if (readingDone && queue.length === 0 && mediaSource) {
        if (mediaSource.readyState === 'open') {
          mediaSource.endOfStream();
        }
      }
    });

    const pump = async () => {
      try {
        const { done, value } = await reader!.read();
        if (done) {
          readingDone = true;
          if (sourceBuffer && !sourceBuffer.updating && mediaSource?.readyState === 'open') {
            mediaSource.endOfStream();
          }
          return;
        }
        queue.push(value!);
        if (sourceBuffer && !sourceBuffer.updating) {
          sourceBuffer.appendBuffer(queue.shift()!);
        }
        pump();
      } catch (err) {
        console.error('Stream 读取错误:', err);
        if (mediaSource?.readyState === 'open') {
          mediaSource.endOfStream();
        }
      }
    };
    pump();
  });

  // 自动播放
  await audioEl.value!.play().catch(err => {
    console.warn('Audio play failed:', err);
  });
}

function cleanup() {
  fetchController?.abort();
  fetchController = null;
  reader = null;
  queue = [];
  readingDone = false;
  mediaSource = null;
  sourceBuffer = null;

  if (audioEl.value) {
    audioEl.value.pause();
    if (audioEl.value.src) {
      URL.revokeObjectURL(audioEl.value.src);
      audioEl.value.src = '';
    }
  }
}

watch(
  () => [props.text, props.play],
  ([newText, newPlay]) => {
    if (newPlay && newText.trim()) {
      startStreaming();
    } else {
      cleanup();
    }
  }
);

onBeforeUnmount(() => {
  cleanup();
});
</script>

