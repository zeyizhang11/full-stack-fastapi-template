import {
  Badge,
  Box,
  Flex,
  Grid,
  Text,
} from "@chakra-ui/react"

import { Tooltip } from "@/components/ui/tooltip"

import { QING_COLOR, SHEN_COLOR, WX_COLOR, METHOD_LABEL } from "./constants"
import {
  LIUQIN_KNOWLEDGE,
  LIUSHEN_KNOWLEDGE,
  SHI_YING_KNOWLEDGE,
  XUNKONG_KNOWLEDGE,
} from "./divinationKnowledge"
import type { HexagramInfo, HexagramReading } from "./types"
import { YaoLineShape } from "./YaoLineShape"

// ─── 六亲悬停提示面板 ─────────────────────────────────────────────────────────

function LiuqinTooltipContent({ name }: { name: string }) {
  const k = LIUQIN_KNOWLEDGE[name]
  if (!k) return <Text fontSize="xs">{name}</Text>
  return (
    <Box maxW="220px" p={1}>
      <Text fontWeight="bold" fontSize="sm" mb={1}>{k.title}</Text>
      <Text fontSize="xs" color="gray.300" mb={2}>{k.summary}</Text>
      <Text fontSize="xs" fontWeight="semibold" mb={1}>代表事物：</Text>
      <Box pl={2} mb={2}>
        {k.represents.map((r) => (
          <Text key={r} fontSize="xs" color="gray.200">• {r}</Text>
        ))}
      </Box>
      <Text fontSize="xs"><Text as="span" color="green.300" fontWeight="semibold">旺相时：</Text>{k.favorable}</Text>
      <Text fontSize="xs" mt={1}><Text as="span" color="orange.300" fontWeight="semibold">休囚时：</Text>{k.unfavorable}</Text>
      {k.notes && (
        <Text fontSize="xs" mt={2} color="yellow.300" borderTopWidth={1} borderColor="gray.600" pt={1}>
          ⚠ {k.notes}
        </Text>
      )}
    </Box>
  )
}

// ─── 六神悬停提示面板 ─────────────────────────────────────────────────────────

function LiushenTooltipContent({ name }: { name: string }) {
  const k = LIUSHEN_KNOWLEDGE[name]
  if (!k) return <Text fontSize="xs">{name}</Text>
  return (
    <Box maxW="220px" p={1}>
      <Flex align="center" gap={2} mb={1}>
        <Text fontWeight="bold" fontSize="sm">{k.title}</Text>
        <Badge
          colorScheme={k.nature === "吉" ? "green" : k.nature === "凶" ? "red" : "yellow"}
          fontSize="9px"
        >
          {k.nature}
        </Badge>
      </Flex>
      <Text fontSize="xs" color="gray.300" mb={2}>{k.summary}</Text>
      <Text fontSize="xs" fontWeight="semibold" mb={1}>代表事物：</Text>
      <Box pl={2} mb={2}>
        {k.represents.map((r) => (
          <Text key={r} fontSize="xs" color="gray.200">• {r}</Text>
        ))}
      </Box>
      <Text fontSize="xs"><Text as="span" color="green.300" fontWeight="semibold">逢吉：</Text>{k.auspicious}</Text>
      <Text fontSize="xs" mt={1}><Text as="span" color="red.300" fontWeight="semibold">逢凶：</Text>{k.inauspicious}</Text>
    </Box>
  )
}

// ─── 主组件 ───────────────────────────────────────────────────────────────────

interface HexagramDisplayProps {
  reading: HexagramReading
  hexagrams: Record<string, HexagramInfo> | undefined
}

export function HexagramDisplay({ reading, hexagrams }: HexagramDisplayProps) {
  const gz = reading.ganzhi_info
  const hasChanged = reading.changed_hexagram_number != null

  const mainHexInfo    = hexagrams?.[String(reading.hexagram_number)]
  const changedHexInfo = hasChanged ? hexagrams?.[String(reading.changed_hexagram_number)] : null
  const mainLines      = reading.lines
  const changedLines   = hasChanged
    ? reading.lines.map((v) => (v === 9 ? 8 : v === 6 ? 7 : v))
    : null

  return (
    <Box borderWidth={1} borderRadius="lg" p={5} mt={4} bg="gray.subtle">
      {/* ── 顶部信息 ── */}
      <Flex gap={2} mb={3} flexWrap="wrap" align="center">
        <Text fontSize="xs" color="gray.500">编号：{reading.reading_number}</Text>
        <Badge colorScheme="purple" fontSize="xs">
          {METHOD_LABEL[reading.cast_method] ?? reading.cast_method}
        </Badge>
        {reading.caster_gender && (
          <Badge colorScheme="pink" fontSize="xs">{reading.caster_gender}</Badge>
        )}
        {reading.caster_name && (
          <Badge colorScheme="blue" fontSize="xs">{reading.caster_name}</Badge>
        )}
      </Flex>

      {reading.question && (
        <Text fontWeight="semibold" mb={3} fontSize="sm">占事：{reading.question}</Text>
      )}

      {/* ── 干支时间 ── */}
      {gz && (
        <Box mb={4} p={3} borderWidth={1} borderRadius="md" bg="whiteAlpha.200" fontSize="sm">
          <Grid templateColumns={{ base: "1fr", sm: "auto auto" }} gap={1} columnGap={6}>
            <Text color="gray.600">
              <Text as="span" fontWeight="semibold" mr={1}>公历：</Text>
              {gz.solar}
            </Text>
            <Text color="gray.600">
              <Text as="span" fontWeight="semibold" mr={1}>干支：</Text>
              {gz.year_gz}年 {gz.month_gz}月 {gz.day_gz}日 {gz.hour_gz}时
            </Text>
          </Grid>
          <Tooltip content={<Box maxW="200px" p={1}><Text fontWeight="bold" fontSize="xs" mb={1}>{XUNKONG_KNOWLEDGE.title}</Text><Text fontSize="xs" color="gray.200">{XUNKONG_KNOWLEDGE.description}</Text></Box>}>
            <Text
              color="orange.500"
              fontSize="xs"
              mt={1}
              display="inline-block"
              cursor="help"
              textDecoration="underline dotted"
            >
              旬空：{gz.xunkong.join("、")}
            </Text>
          </Tooltip>
        </Box>
      )}

      {/* ── 卦名标题行 ── */}
      <Flex gap={4} mb={2} fontSize="sm" fontWeight="semibold" color="gray.700">
        <Box style={{ flex: 1 }}>
          {mainHexInfo && (
            <Text>
              本卦：{reading.palace ? `${reading.palace}宫 ` : ""}
              {mainHexInfo.zh}（{mainHexInfo.pinyin}）
            </Text>
          )}
        </Box>
        {hasChanged && (
          <Box style={{ flex: 1 }}>
            {changedHexInfo && (
              <Text>
                变卦：{reading.changed_palace ? `${reading.changed_palace}宫 ` : ""}
                {changedHexInfo.zh}（{changedHexInfo.pinyin}）
              </Text>
            )}
          </Box>
        )}
      </Flex>

      {/* ── 统一对齐表格 ── */}
      <Box overflowX="auto">
        <table style={{ borderCollapse: "collapse", fontSize: "13px", width: "100%" }}>
          <colgroup>
            <col style={{ width: "52px" }} />{/* 六神 */}
            <col style={{ width: "88px" }} />{/* 伏神 */}
            <col style={{ minWidth: "108px" }} />{/* 六亲纳甲 本 */}
            <col style={{ width: "96px" }} />{/* 爻线 本 */}
            <col style={{ width: "28px" }} />{/* 世应 本 */}
            {hasChanged && (
              <>
                <col style={{ width: "8px" }} />
                <col style={{ minWidth: "108px" }} />
                <col style={{ width: "96px" }} />
                <col style={{ width: "28px" }} />
              </>
            )}
          </colgroup>
          <thead>
            <tr style={{ fontSize: "11px", color: "#718096", borderBottom: "1px solid #e2e8f0" }}>
              <th style={{ fontWeight: 500, textAlign: "center", paddingBottom: "4px" }}>六神</th>
              <th style={{ fontWeight: 500, textAlign: "center", paddingBottom: "4px", color: "#a0aec0" }}>伏神</th>
              <th style={{ fontWeight: 500, textAlign: "left", paddingBottom: "4px" }}>六亲 纳甲</th>
              <th style={{ fontWeight: 500, textAlign: "center", paddingBottom: "4px" }}>爻线</th>
              <th style={{ fontWeight: 500, textAlign: "center", paddingBottom: "4px" }}>位</th>
              {hasChanged && (
                <>
                  <th />
                  <th style={{ fontWeight: 500, textAlign: "left", paddingLeft: "8px", paddingBottom: "4px" }}>
                    六亲 纳甲
                  </th>
                  <th style={{ fontWeight: 500, textAlign: "center", paddingBottom: "4px" }}>爻线</th>
                  <th style={{ fontWeight: 500, textAlign: "center", paddingBottom: "4px" }}>位</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {[5, 4, 3, 2, 1, 0].map((idx) => {
              const yi          = reading.yao_info?.[idx]
              const cy          = reading.changed_yao_info?.[idx]
              const lineV       = mainLines[idx]
              const changedLineV = changedLines?.[idx]
              const isShi   = reading.shi_yao         === idx + 1
              const isYing  = reading.ying_yao         === idx + 1
              const isCshi  = reading.changed_shi_yao  === idx + 1
              const isCying = reading.changed_ying_yao === idx + 1

              return (
                <tr key={idx} style={{ lineHeight: "2.2" }}>

                  {/* 六神 — 悬停显示六神含义 */}
                  <td style={{ textAlign: "center", paddingRight: "4px" }}>
                    {yi && (
                      <Tooltip
                        content={<LiushenTooltipContent name={yi.liushen} />}
                        positioning={{ placement: "right" }}
                      >
                        <Badge
                          colorScheme={SHEN_COLOR[yi.liushen]}
                          variant="subtle"
                          fontSize="xs"
                          px={1}
                          cursor="help"
                        >
                          {yi.liushen}
                        </Badge>
                      </Tooltip>
                    )}
                  </td>

                  {/* 伏神 */}
                  <td style={{ textAlign: "center", paddingRight: "4px", opacity: 0.65 }}>
                    {yi?.fuxin && (
                      <Text fontSize="xs" color="gray.500" whiteSpace="nowrap">
                        <Tooltip content={<LiuqinTooltipContent name={yi.fuxin.liuqin} />} positioning={{ placement: "right" }}>
                          <Badge colorScheme="gray" variant="subtle" fontSize="9px" mr="1" cursor="help">
                            {yi.fuxin.liuqin}
                          </Badge>
                        </Tooltip>
                        {yi.fuxin.ganzhi}
                      </Text>
                    )}
                  </td>

                  {/* 本卦：六亲 + 纳甲 — 悬停显示六亲含义 */}
                  <td style={{ paddingRight: "6px" }}>
                    {yi && (
                      <Text fontSize="xs" whiteSpace="nowrap">
                        <Tooltip
                          content={<LiuqinTooltipContent name={yi.liuqin} />}
                          positioning={{ placement: "right" }}
                        >
                          <Badge
                            colorScheme={QING_COLOR[yi.liuqin]}
                            variant="subtle"
                            fontSize="9px"
                            mr="1"
                            cursor="help"
                          >
                            {yi.liuqin}
                          </Badge>
                        </Tooltip>
                        <Text
                          as="span"
                          color={yi.is_xunkong ? "gray.400" : "gray.800"}
                          textDecoration={yi.is_xunkong ? "line-through" : "none"}
                        >
                          {yi.najia}
                        </Text>
                        <Text as="span" color={WX_COLOR[yi.element]} ml={1} fontSize="9px">
                          ({yi.element})
                        </Text>
                        {yi.is_xunkong && (
                          <Tooltip content={<Box maxW="180px" p={1}><Text fontWeight="bold" fontSize="xs" mb={1}>{XUNKONG_KNOWLEDGE.title}</Text><Text fontSize="xs" color="gray.200">{XUNKONG_KNOWLEDGE.description}</Text></Box>}>
                            <Text as="span" fontSize="9px" color="gray.400" ml={1} cursor="help">
                              (空)
                            </Text>
                          </Tooltip>
                        )}
                      </Text>
                    )}
                  </td>

                  {/* 本卦：爻线 */}
                  <td style={{ padding: "2px 8px" }}>
                    <YaoLineShape value={lineV} xunkong={yi?.is_xunkong ?? false} />
                  </td>

                  {/* 本卦：世/应 — 悬停显示世应含义 */}
                  <td style={{ textAlign: "center" }}>
                    {isShi && (
                      <Tooltip content={<Box maxW="200px" p={1}><Text fontWeight="bold" fontSize="xs" mb={1}>{SHI_YING_KNOWLEDGE.shi.title}</Text><Text fontSize="xs" color="gray.200">{SHI_YING_KNOWLEDGE.shi.description}</Text></Box>}>
                        <Badge colorScheme="purple" fontSize="xs" cursor="help">世</Badge>
                      </Tooltip>
                    )}
                    {isYing && (
                      <Tooltip content={<Box maxW="200px" p={1}><Text fontWeight="bold" fontSize="xs" mb={1}>{SHI_YING_KNOWLEDGE.ying.title}</Text><Text fontSize="xs" color="gray.200">{SHI_YING_KNOWLEDGE.ying.description}</Text></Box>}>
                        <Badge colorScheme="teal" fontSize="xs" cursor="help">应</Badge>
                      </Tooltip>
                    )}
                  </td>

                  {hasChanged && (
                    <>
                      {/* 分隔线 */}
                      <td style={{ borderLeft: "1px solid #e2e8f0" }} />

                      {/* 变卦：六亲 + 纳甲 */}
                      <td style={{ paddingLeft: "8px", paddingRight: "6px" }}>
                        {cy && (
                          <Text fontSize="xs" whiteSpace="nowrap">
                            <Tooltip
                              content={<LiuqinTooltipContent name={cy.liuqin} />}
                              positioning={{ placement: "left" }}
                            >
                              <Badge
                                colorScheme={QING_COLOR[cy.liuqin]}
                                variant="subtle"
                                fontSize="9px"
                                mr="1"
                                cursor="help"
                              >
                                {cy.liuqin}
                              </Badge>
                            </Tooltip>
                            <Text
                              as="span"
                              color={cy.is_xunkong ? "gray.400" : "gray.800"}
                              textDecoration={cy.is_xunkong ? "line-through" : "none"}
                            >
                              {cy.najia}
                            </Text>
                            <Text as="span" color={WX_COLOR[cy.element]} ml={1} fontSize="9px">
                              ({cy.element})
                            </Text>
                          </Text>
                        )}
                      </td>

                      {/* 变卦：爻线 */}
                      <td style={{ padding: "2px 8px" }}>
                        {changedLineV !== undefined && (
                          <YaoLineShape value={changedLineV} xunkong={cy?.is_xunkong ?? false} />
                        )}
                      </td>

                      {/* 变卦：世/应 */}
                      <td style={{ textAlign: "center" }}>
                        {isCshi && (
                          <Tooltip content={<Box maxW="200px" p={1}><Text fontWeight="bold" fontSize="xs" mb={1}>{SHI_YING_KNOWLEDGE.shi.title}</Text><Text fontSize="xs" color="gray.200">{SHI_YING_KNOWLEDGE.shi.description}</Text></Box>}>
                            <Badge colorScheme="purple" fontSize="xs" cursor="help">世</Badge>
                          </Tooltip>
                        )}
                        {isCying && (
                          <Tooltip content={<Box maxW="200px" p={1}><Text fontWeight="bold" fontSize="xs" mb={1}>{SHI_YING_KNOWLEDGE.ying.title}</Text><Text fontSize="xs" color="gray.200">{SHI_YING_KNOWLEDGE.ying.description}</Text></Box>}>
                            <Badge colorScheme="teal" fontSize="xs" cursor="help">应</Badge>
                          </Tooltip>
                        )}
                      </td>
                    </>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      </Box>

      {/* 卦辞 */}
      {mainHexInfo && (
        <Text fontSize="xs" color="gray.500" mt={3}>{mainHexInfo.judgment}</Text>
      )}
    </Box>
  )
}
