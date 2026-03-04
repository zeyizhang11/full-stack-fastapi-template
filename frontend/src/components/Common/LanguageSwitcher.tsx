/**
 * LanguageSwitcher — 语言切换下拉菜单
 * 放在 Navbar 右侧，支持中文 / English / العربية
 */
import { Button, Menu, Portal, Text } from "@chakra-ui/react"
import { useTranslation } from "react-i18next"

import { SUPPORTED_LANGUAGES, type LangCode } from "@/i18n"

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation()

  const current = SUPPORTED_LANGUAGES.find((l) => l.code === i18n.language)
    ?? SUPPORTED_LANGUAGES[0]

  function handleChange(code: LangCode) {
    i18n.changeLanguage(code)
  }

  return (
    <Menu.Root>
      <Menu.Trigger asChild>
        <Button variant="ghost" size="sm" aria-label={t("common.language")}>
          <Text fontSize="lg" mr={1}>{current.flag}</Text>
          <Text fontSize="sm" display={{ base: "none", md: "inline" }}>
            {current.label}
          </Text>
        </Button>
      </Menu.Trigger>
      <Portal>
        <Menu.Positioner>
          <Menu.Content minW="140px">
            {SUPPORTED_LANGUAGES.map((lang) => (
              <Menu.Item
                key={lang.code}
                value={lang.code}
                onClick={() => handleChange(lang.code as LangCode)}
                fontWeight={lang.code === i18n.language ? "bold" : "normal"}
                color={lang.code === i18n.language ? "teal.500" : undefined}
              >
                <Text mr={2} fontSize="lg">{lang.flag}</Text>
                {lang.label}
              </Menu.Item>
            ))}
          </Menu.Content>
        </Menu.Positioner>
      </Portal>
    </Menu.Root>
  )
}
