// 极简 Pub/Sub：无第三方依赖
export type TtsEvent = 'tts:start' | 'tts:delta' | 'tts:end' | 'tts:stop';
type Handler = (payload?: any) => void;

const map = new Map<TtsEvent, Set<Handler>>();

export const ttsBus = {
  on(type: TtsEvent, fn: Handler) {
    if (!map.has(type)) map.set(type, new Set());
    map.get(type)!.add(fn);
    return () => map.get(type)!.delete(fn); // 返回 off 函数
  },
  off(type: TtsEvent, fn: Handler) {
    map.get(type)?.delete(fn);
  },
  emit(type: TtsEvent, payload?: any) {
    map.get(type)?.forEach(fn => {
      try { fn(payload); } catch (e) { console.error('[ttsBus]', e); }
    });
  }
};
