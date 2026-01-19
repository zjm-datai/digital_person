// frontend/src/composables/useThinkParser.ts

export interface ThinkDelta {
  visibleDelta: string;
  thinkingDelta: string;
}

type Mode = "visible" | "thinking";

interface ParserState {
  mode: Mode;
  carry: string;      // 承接可能被切开的标签片段
  swallowLf: number;  // </think> 后吞换行剩余次数
}

const OPEN = "<think>";
const CLOSE = "</think>";

function isNewlineStart(s: string, i: number) {
  return s.startsWith("\r\n", i) || s.startsWith("\n", i);
}

function consumeOneNewline(s: string, i: number) {
  if (s.startsWith("\r\n", i)) return i + 2;
  if (s.startsWith("\n", i)) return i + 1;
  return i;
}

/**
 * 增量解析：输入 chunk + state(carry/mode/swallowLf)，输出本次 delta
 * - 支持 <think> / </think> 被拆分在多个 chunk
 * - 支持吞掉 </think> 后最多 N 个换行（默认 2）
 */
function parseChunk(input: string, st: ParserState, swallowAfterCloseMax: number): ThinkDelta {
  let visible = "";
  let thinking = "";

  // 拼上上次残留
  let s = (st.carry || "") + (input || "");
  st.carry = "";

  let i = 0;
  const maxTagLen = Math.max(OPEN.length, CLOSE.length);

  while (i < s.length) {
    // 1) 吞 </think> 后的换行
    if (st.swallowLf > 0) {
      if (isNewlineStart(s, i)) {
        i = consumeOneNewline(s, i);
        st.swallowLf -= 1;
        continue;
      } else {
        st.swallowLf = 0;
      }
    }

    // 2) 剩余不够判断标签：如果疑似标签开头，则 carry 起来
    const remain = s.length - i;
    if (remain < maxTagLen) {
      if (s[i] === "<") {
        st.carry = s.slice(i);
        break;
      }
      const ch = s[i++];
      if (st.mode === "thinking") thinking += ch;
      else visible += ch;
      continue;
    }

    // 3) 完整标签匹配
    if (s.startsWith(OPEN, i)) {
      st.mode = "thinking";
      i += OPEN.length;
      continue;
    }
    if (s.startsWith(CLOSE, i)) {
      st.mode = "visible";
      i += CLOSE.length;
      st.swallowLf = swallowAfterCloseMax;
      continue;
    }

    // 4) 普通字符
    const ch = s[i++];
    if (st.mode === "thinking") thinking += ch;
    else visible += ch;
  }

  return { visibleDelta: visible, thinkingDelta: thinking };
}

export function createThinkAccumulator(opts?: { swallowAfterClose?: number }) {
  const swallowAfterClose = Math.max(0, Math.min(5, opts?.swallowAfterClose ?? 2));
  const map = new Map<number, ParserState>();

  function reset(index: number) {
    map.set(index, { mode: "visible", carry: "", swallowLf: 0 });
  }

  function ingest(index: number, chunk: string): ThinkDelta {
    if (!map.has(index)) reset(index);
    const st = map.get(index)!;
    return parseChunk(chunk ?? "", st, swallowAfterClose);
  }

  return { ingest, reset };
}
