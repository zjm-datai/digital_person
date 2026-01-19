// src/utils/textNormalize.ts

/** 只保证前后无空格/换行，不修改中间内容 */
export function trimEnds(s: string): string {
  return (s ?? "").replace(/^\s+|\s+$/g, "");
}

/** 拼接后立刻做 trimEnds，保证每次写入字段都是干净的 */
export function appendAndTrim(prev: string, delta: string): string {
  return trimEnds((prev ?? "") + (delta ?? ""));
}
