// ─── 颜色映射常量 ──────────────────────────────────────────────────────────────

/** 六神对应颜色 */
export const SHEN_COLOR: Record<string, string> = {
  青龙: "blue",
  朱雀: "red",
  勾陈: "yellow",
  腾蛇: "orange",
  白虎: "gray",
  玄武: "purple",
}

/** 六亲对应颜色 */
export const QING_COLOR: Record<string, string> = {
  父母: "blue",
  兄弟: "gray",
  妻财: "yellow",
  子孙: "green",
  官鬼: "red",
}

/** 五行对应颜色 */
export const WX_COLOR: Record<string, string> = {
  金: "yellow",
  木: "green",
  水: "blue",
  火: "red",
  土: "orange",
}

/** 起卦方式标签 */
export const METHOD_LABEL: Record<string, string> = {
  coin: "三铜钱法",
  time: "时间起卦",
  numbers: "报数起卦",
  manual: "手动填爻",
}

/** 手动填爻选项 */
export const LINE_OPTIONS = [
  { value: 7, label: "7 — 少阳（实线）" },
  { value: 8, label: "8 — 少阴（虚线）" },
  { value: 9, label: "9 — 老阳（实线，变）" },
  { value: 6, label: "6 — 老阴（虚线，变）" },
]

// ─── API 助手 ──────────────────────────────────────────────────────────────────

export const API_BASE = import.meta.env.VITE_API_URL ?? ""

export function getToken() {
  return localStorage.getItem("access_token")
}

export function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}
