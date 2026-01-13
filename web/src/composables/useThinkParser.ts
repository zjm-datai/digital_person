// frontend/src/composables/useThinkParser.ts

export interface ThinkDelta {
    visibleDelta: string;
    thinkingDelta: string;
}

interface AccState {
    raw: string;          // 累计到目前为止的原始串
    visibleLen: number;   // 已消费的“可见”长度
    thinkingLen: number;  // 已消费的“思考”长度
}

function parseAll(raw: string): { visible: string; thinking: string } {
  let visible = "";
  let thinking = "";
  let i = 0;
  let inThink = false;

  while (i < raw.length) {
    if (raw.startsWith("<think>", i)) {
      inThink = true;
      i += 7;
      continue;
    }

    if (raw.startsWith("</think>", i)) {
      inThink = false;
      i += 8;

      // ✅ 吞掉 </think> 后紧跟的换行（最多吞 2 个 \n；兼容 \r\n）
      // 目标：去掉你看到的 </think>\n\n
      if (raw.startsWith("\r\n", i)) {
        i += 2;
      } else if (raw.startsWith("\n", i)) {
        i += 1;
      }

      // 第二个换行（如果存在）
      if (raw.startsWith("\r\n", i)) {
        i += 2;
      } else if (raw.startsWith("\n", i)) {
        i += 1;
      }

      continue;
    }

    const ch = raw[i];
    if (inThink) thinking += ch;
    else visible += ch;

    i++;
  }

  return { visible, thinking };
}

/**
 * 为每条消息索引维护一个解析状态
 */
export function createThinkAccumulator() {
    const map: Record<number, AccState> = {};

    function reset(index: number) {
        map[index] = { raw: "", visibleLen: 0, thinkingLen: 0 };
    }

    function ingest(index: number, chunk: string): ThinkDelta {
        if (!map[index]) reset(index);

        // 1) 累加原始串
        map[index].raw += chunk;

        // 2) 以“完整累积串”做解析，得到当前完整的可见/思考
        const parsed = parseAll(map[index].raw);

        // 3) 计算 delta：把本次比上次多出来的那一截返回
        const vLenPrev = map[index].visibleLen;
        const tLenPrev = map[index].thinkingLen;

        const visibleDelta = parsed.visible.slice(vLenPrev);
        const thinkingDelta = parsed.thinking.slice(tLenPrev);

        // 4) 更新“已消费长度”
        map[index].visibleLen = parsed.visible.length;
        map[index].thinkingLen = parsed.thinking.length;

        return { visibleDelta, thinkingDelta };
    }

    return { ingest, reset };
}
