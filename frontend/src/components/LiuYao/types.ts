// ─── LiuYao 公共 TypeScript 类型定义 ──────────────────────────────────────────

export interface GanzhiInfo {
  solar: string
  year_gz: string
  month_gz: string
  day_gz: string
  hour_gz: string
  xunkong: string[]
}

export interface YaoInfo {
  liuqin: string
  najia: string
  element: string
  liushen: string
  is_shi: boolean
  is_ying: boolean
  is_xunkong: boolean
  fuxin: { ganzhi: string; liuqin: string } | null
}

export interface HexagramReading {
  id: string
  reading_number: string
  cast_method: string
  question: string | null
  caster_name: string | null
  caster_gender: string | null
  lines: number[]
  hexagram_number: number
  changed_hexagram_number: number | null
  created_at: string
  owner_id: string | null
  // 批注字段
  ganzhi_info?: GanzhiInfo
  palace?: string
  palace_element?: string
  shi_yao?: number
  ying_yao?: number
  yao_info?: YaoInfo[]
  // 变卦批注
  changed_palace?: string
  changed_shi_yao?: number
  changed_ying_yao?: number
  changed_yao_info?: YaoInfo[]
}

export interface HexagramInfo {
  zh: string
  pinyin: string
  en: string
  judgment: string
}

export interface UserInfoFields {
  caster_name?: string
  caster_gender?: string
  question?: string
}

export interface TimeFormValues extends UserInfoFields {
  year: number
  month: number
  day: number
  hour: number
}

export interface NumbersFormValues extends UserInfoFields {
  upper_num: number
  lower_num: number
  changing_num: number
}

export interface ManualFormValues extends UserInfoFields {
  line1: number
  line2: number
  line3: number
  line4: number
  line5: number
  line6: number
}
