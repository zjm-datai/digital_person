<template>
  <audio ref="audioEl" hidden playsinline></audio>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { ttsBus } from '@/bus/ttsBus';

interface Props {
  wsUri?: string;
  voice?: string;
  format?: 'mp3'|'wav'|'ogg'|'opus'|'pcm';
  sampleRate?: number;
  speed?: number;
  mode?: 'stream'|'one_shot';
  autoplay?: boolean;
}

// const props = withDefaults(defineProps<Props>(), {
//   wsUri: 'ws://211.90.240.240:30055/v1/ws/audio/speech', // 若无 /v1 网关，请改成 /ws/audio/speech
//   voice: 'doctor_woman',
//   format: 'pcm',
//   sampleRate: 24000,
//   speed: 1.0,
//   mode: 'stream',
//   autoplay: true,
// });

const props = withDefaults(defineProps<Props>(), {
  // 关键修改：ws:// → wss://，IP:端口 → 前端页面域名（maas.ningtanghealth.com）
  wsUri: 'wss://maas.ningtanghealth.com/v1/ws/audio/speech', 
  // wsUri: 'ws://211.90.240.240:30055/v1/ws/audio/speech',
  voice: 'haiwenyuan',
  format: 'pcm',
  sampleRate: 24000,
  speed: 1.0,
  mode: 'stream',
  autoplay: true,
});

/* -------------------- 公共状态 -------------------- */
let ws: WebSocket | null = null;
const audioEl = ref<HTMLAudioElement>();
let haveStart = false;           // 是否收到 start
let ending = false;

/* 在 start 之前收到的二进制先缓存，待确定格式后再处理 */
const preStartBin: Uint8Array[] = [];

/* -------------------- MP3（MSE）路径 -------------------- */
let mediaSource: MediaSource | null   = null;
let sourceBuffer: SourceBuffer | null = null;
let mseOpen = false;
let mp3Mime = 'audio/mpeg';
let mp3Queue: Uint8Array[] = []; // SB updating 时暂存

function ensureMSE() {
  if (mediaSource) return;
  mediaSource = new MediaSource();
  audioEl.value!.src = URL.createObjectURL(mediaSource);
  mediaSource.addEventListener('sourceopen', () => {
    mseOpen = true;
    // 真正创建 SB 延后到收到 start 知道最终 mime 后
  });
}

function createSBIfNeeded(mime: string) {
  if (!mediaSource || sourceBuffer) return;
  if (!('MediaSource' in window) || !MediaSource.isTypeSupported(mime)) {
    console.error('[WebsocketTTS] MIME not supported by MSE:', mime);
    return;
  }
  try {
    sourceBuffer = mediaSource.addSourceBuffer(mime);
    sourceBuffer.mode = 'sequence';
    sourceBuffer.addEventListener('updateend', flushMp3Queue);
    // 把 preStartBin（若有）与 mp3Queue 一并送入
    while (preStartBin.length) mp3Queue.push(preStartBin.shift()!);
    flushMp3Queue();
  } catch (e) {
    console.error('[WebsocketTTS] addSourceBuffer failed:', e);
  }
}

function appendMp3(chunk: Uint8Array) {
  if (!sourceBuffer) { mp3Queue.push(chunk); return; }
  if (sourceBuffer.updating) { mp3Queue.push(chunk); return; }
  try { sourceBuffer.appendBuffer(chunk); }
  catch (e) { mp3Queue.push(chunk); }
}

function flushMp3Queue() {
  if (!sourceBuffer || sourceBuffer.updating) return;
  if (mp3Queue.length) {
    const c = mp3Queue.shift()!;
    try { sourceBuffer.appendBuffer(c); }
    catch (e) { mp3Queue.unshift(c); }
  } else if (ending && mediaSource?.readyState === 'open') {
    try { mediaSource.endOfStream(); } catch {}
  }
}

/* -------------------- PCM（WebAudio）路径 -------------------- */
type Ctx = (AudioContext & { resume?: () => Promise<void> }) | null;
let audioCtx: Ctx = null;
let gainNode: GainNode | null = null;
let pcmSampleRate = props.sampleRate;
let timeCursor = 0; // 排程播放的时间光标（AudioContext.currentTime 为基准）

function ensureAudioCtx(sr: number) {
  if (!audioCtx || Math.abs((audioCtx as any).sampleRate - sr) > 1) {
    if (audioCtx) { try { audioCtx.close(); } catch {} }
    const AC = (window.AudioContext || (window as any).webkitAudioContext);
    audioCtx = new AC({ sampleRate: sr });
    gainNode = audioCtx.createGain();
    gainNode.connect(audioCtx.destination);
    timeCursor = audioCtx.currentTime + 0.05; // 50ms 预滚
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume?.().catch(()=>{});
  }
}

function playPcmChunk(u8: Uint8Array) {
  if (!u8?.length) return;
  ensureAudioCtx(pcmSampleRate!);

  const frameCount = (u8.byteLength / 2) | 0; // s16le 单声道
  if (frameCount <= 0 || !audioCtx) return;

  const f32 = new Float32Array(frameCount);
  const dv  = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
  for (let i = 0; i < frameCount; i++) {
    const s = dv.getInt16(i * 2, true);
    // 映射到 [-1,1]，保持对称
    f32[i] = s < 0 ? s / 32768 : s / 32767;
  }

  const buf = audioCtx.createBuffer(1, frameCount, pcmSampleRate!);
  buf.getChannelData(0).set(f32);

  const src = audioCtx.createBufferSource();
  src.buffer = buf;
  src.connect(gainNode!);

  const startAt = Math.max(audioCtx.currentTime + 0.005, timeCursor);
  try { src.start(startAt); } catch (e) { /* 某些时序下会抛，忽略 */ }
  timeCursor = startAt + buf.duration;
}

/* -------------------- WS 建连与消息处理 -------------------- */
function wsInitConfig() {
  return {
    voice: props.voice,
    response_format: props.format,   // 你传 mp3/wav/pcm；后端若收到 wav 会转 pcm
    speed: props.speed,
    sample_rate: props.sampleRate,
    mode: props.mode,
  };
}

function connect() {
  // cleanup(true); // 不发 eof，清理旧实例
  console.info('[WebsocketTTS] connect ->', props.wsUri);
  try { ws = new WebSocket(props.wsUri); } catch (e) {
    console.error('[WebsocketTTS] new WebSocket() failed:', e); return;
  }
  ws.binaryType = 'arraybuffer';
  haveStart = false;
  ending = false;

  ws.onopen = () => {
    ws?.send(JSON.stringify(wsInitConfig()));
    // 只在 mp3 路径会用到 MSE；但此处可先准备好，真正创建 SB 等 start 后决定
    ensureMSE();
    if (props.autoplay) {
      // mp3 通过 <audio>；pcm 通过 AudioContext
      audioEl.value?.play().catch(()=>{});
    }
  };

  ws.onmessage = (evt) => {
    if (typeof evt.data === 'string') {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === 'start') {
          haveStart = true;
          const fmt = String(msg.format || props.format || '').toLowerCase();
          const mime = String(msg.mime || '').toLowerCase();
          const sr   = Number(msg.sample_rate || props.sampleRate || 24000);

          console.log("msg: ", msg);

          if (fmt === 'wav') { // 按你后端逻辑，wav 会转成 pcm
            handleStartPCM(sr);
          } else if (fmt === 'pcm') {
            handleStartPCM(sr);
          } else if (fmt === 'mp3') {
            handleStartMP3(mime || 'audio/mpeg');
          } else {
            // 其它格式按 mp3 处理（大多也是压缩容器）
            handleStartMP3(mime || 'audio/mpeg');
          }

          // 把 preStartBin（若有）按对应路径处理
          if (preStartBin.length) {
            const tmp = preStartBin.splice(0, preStartBin.length);
            for (const c of tmp) {
              if (isPCM()) playPcmChunk(c);
              else appendMp3(c);
            }
          }
        } else if (msg.type === 'end') {
          ending = true;
          if (!isPCM() && mediaSource?.readyState === 'open') {
            flushMp3Queue();
            try { mediaSource.endOfStream(); } catch {}
          }
        } else if (msg.type === 'ping') {
          // ignore
        } else if (msg.type === 'error') {
          console.error('[WebsocketTTS] server error:', msg.message);
        }
      } catch {
        // 非 JSON 文本帧（极少），忽略
      }
    } else {
      const u8 = new Uint8Array(evt.data as ArrayBuffer);
      if (!haveStart) {
        preStartBin.push(u8);
      } else {
        if (isPCM()) {
          console.log("is pcm audio")
          playPcmChunk(u8);
        }
        else appendMp3(u8);
      }
    }
  };

  ws.onerror = (e) => console.info('[WebsocketTTS] ws error', e);
  // ws.onclose  = (e) => { console.info('[WebsocketTTS] ws close', e.code, e.reason); cleanup(); };
}

/* ——— start 分支 ——— */
function isPCM() { return !!audioCtx; } // 是否走 PCM 路径

function handleStartPCM(sr: number) {
  // 关闭 mp3 相关（如已存在）
  if (sourceBuffer) { try { sourceBuffer.removeEventListener('updateend', flushMp3Queue); } catch {} }
  sourceBuffer = null;

  pcmSampleRate = sr || props.sampleRate || 24000;
  ensureAudioCtx(pcmSampleRate);
}

function handleStartMP3(mime: string) {
  // 确保不用 AudioContext（PCM）路径
  if (audioCtx) { try { audioCtx.close(); } catch {} audioCtx = null; gainNode = null; }

  mp3Mime = mime || 'audio/mpeg';
  ensureMSE();
  if (mseOpen) createSBIfNeeded(mp3Mime);
}

/* -------------------- 文本事件 → 直接透传 -------------------- */
const pendingText: string[] = []; // 建连前积压的增量文本
function pushDelta(delta: string) {
  if (!delta) return;
  if (!ws || ws.readyState !== WebSocket.OPEN) { pendingText.push(delta); return; }
  try { ws.send(JSON.stringify({ type: 'text', data: delta })); }
  catch (e) { pendingText.push(delta); }
}
function end() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    try { ws.send(JSON.stringify({ type: 'eof' })); } catch {}
    ending = true;
  }
}

/* -------------------- 清理 -------------------- */
function cleanup(skipEof = false) {
  try { if (!skipEof) end(); } catch {}
  try { ws?.close(); } catch {}
  ws = null;

  haveStart = false;
  ending = false;
  preStartBin.length = 0;

  // MP3/MSE
  mp3Queue = [];
  mseOpen = false;
  if (sourceBuffer) { try { sourceBuffer.removeEventListener('updateend', flushMp3Queue); } catch {} }
  sourceBuffer = null;
  if (mediaSource) {
    try { if (mediaSource.readyState === 'open') mediaSource.endOfStream(); } catch {}
    mediaSource = null;
  }
  if (audioEl.value) {
    try { audioEl.value.pause(); } catch {}
    if (audioEl.value.src) { try { URL.revokeObjectURL(audioEl.value.src); } catch {} audioEl.value.src = ''; }
  }

  // PCM/WebAudio
  if (audioCtx) { try { audioCtx.close(); } catch {} audioCtx = null; }
  gainNode = null;

  // 文本缓存
  // 不清 pendingText，允许建连后补发；如需丢弃可改为清空
}

/* -------------------- 事件总线 -------------------- */
let offs: Array<() => void> = [];
onMounted(() => {
  offs.push(ttsBus.on('tts:start', () => {
    connect();
    // 建连前已堆积的文本帧补发
    if (pendingText.length) {
      const list = pendingText.splice(0, pendingText.length);
      for (const seg of list) pushDelta(seg);
    }
  }));
  offs.push(ttsBus.on('tts:delta', (delta) => pushDelta(String(delta ?? ''))));
  offs.push(ttsBus.on('tts:end',   () => end()));
  offs.push(ttsBus.on('tts:stop',  () => cleanup()));
});
onBeforeUnmount(() => { offs.forEach(off => off()); cleanup(); });
</script>
