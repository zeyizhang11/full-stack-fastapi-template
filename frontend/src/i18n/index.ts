import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

import ar from "./locales/ar.json"
import en from "./locales/en.json"
import zh from "./locales/zh.json"

export const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English", flag: "🇺🇸" },
  { code: "zh", label: "中文",    flag: "🇨🇳" },
  { code: "ar", label: "العربية", flag: "🇸🇦", rtl: true },
] as const

export type LangCode = (typeof SUPPORTED_LANGUAGES)[number]["code"]

i18n
  .use(LanguageDetector)        // 自动检测浏览器语言
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
      ar: { translation: ar },
    },
    fallbackLng: "en",
    supportedLngs: ["en", "zh", "ar"],
    interpolation: {
      escapeValue: false,       // React 已自动转义
    },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "i18nLang",
    },
  })

/** 切换语言时同步处理 RTL/LTR 方向 */
export function applyDirection(lng: string) {
  const isRtl = SUPPORTED_LANGUAGES.find((l) => l.code === lng)?.rtl ?? false
  document.documentElement.dir = isRtl ? "rtl" : "ltr"
  document.documentElement.lang = lng
}

i18n.on("languageChanged", applyDirection)

// 首次加载时应用
applyDirection(i18n.language)

export default i18n
