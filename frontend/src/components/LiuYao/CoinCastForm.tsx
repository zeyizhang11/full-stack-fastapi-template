/**
 * CoinCastForm — 三铜钱法起卦（逐爻动画版）
 *
 * 用户流程：
 *  1. 填写姓名 / 性别 / 占事（均可选填）
 *  2. 点击"开始摇"——三枚铜钱剧烈抖动，面值快速随机翻转
 *  3. 点击"停止"   ——铜钱立定，展示本次落点（正/反），当爻爻线出现
 *  4. 重复 6 次后，点击"提交起卦"——调用 /cast/manual 接口并回调 onResult
 */

import { useMutation } from "@tanstack/react-query"
import axios from "axios"
import { useEffect, useRef, useState } from "react"
import { useForm } from "react-hook-form"

import {
  Box,
  Flex,
  Grid,
  Input,
  NativeSelect,
  Stack,
  Text,
} from "@chakra-ui/react"

import { Button } from "@/components/ui/button"

// ─── Constants ─────────────────────────────────────────────────────────────

const API_BASE = import.meta.env.VITE_API_URL ?? ""

function getToken() {
  return localStorage.getItem("access_token")
}
function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// ─── Global animation styles (injected once) ─────────────────────────────────

const STYLE_ID = "coin-cast-keyframes"

function injectKeyframes() {
  if (document.getElementById(STYLE_ID)) return
  const style = document.createElement("style")
  style.id = STYLE_ID
  style.textContent = `
    @keyframes coinShake {
      0%   { transform: translate(0,    0)    rotate(0deg);  }
      15%  { transform: translate(-4px, 3px)  rotate(-6deg); }
      30%  { transform: translate(4px,  -3px) rotate(5deg);  }
      45%  { transform: translate(-3px, -4px) rotate(-4deg); }
      60%  { transform: translate(3px,  4px)  rotate(6deg);  }
      75%  { transform: translate(-2px, 2px)  rotate(-3deg); }
      90%  { transform: translate(2px,  -2px) rotate(3deg);  }
      100% { transform: translate(0,    0)    rotate(0deg);  }
    }
    @keyframes yaoReveal {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0);   }
    }
  `
  document.head.appendChild(style)
}

// ─── Types ───────────────────────────────────────────────────────────────────

type CoinFace = "正" | "反"
/** 爻值：6=老阴·变, 7=少阳, 8=少阴, 9=老阳·变 */
type YaoValue = 6 | 7 | 8 | 9

interface CoinFormValues {
  caster_name?: string
  caster_gender?: string
  question?: string
}

// onResult 接受后端返回的卦象，用 any 避免循环依赖类型文件
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function CoinCastForm({ onResult }: { onResult: (r: any) => void }) {
  const { register, getValues } = useForm<CoinFormValues>()

  // 注入 CSS 动画
  useEffect(() => {
    injectKeyframes()
  }, [])

  // ── 状态 ──────────────────────────────────────────────────────────────────
  /** 已定的六爻，index 0 = 第一爻（最底），最多 6 个 */
  const [yaos, setYaos] = useState<YaoValue[]>([])
  /** 当前是否正在摇动 */
  const [shaking, setShaking] = useState(false)
  /**
   * 点击"开始摇"时立即生成的本爻结果（先存下来，停止时才展示）
   */
  const [pendingResult, setPendingResult] = useState<{
    faces: CoinFace[]
    yaoValue: YaoValue
  } | null>(null)
  /** 铜钱当前显示的面值（摇动时快速闪烁） */
  const [displayFaces, setDisplayFaces] = useState<CoinFace[]>(["正", "正", "正"])

  const shakeIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const isDone = yaos.length === 6
  const currentYaoIdx = yaos.length // 0-based，下一爻的序号

  // ── 工具函数 ──────────────────────────────────────────────────────────────

  /** 随机抛三枚铜钱，算出爻值 */
  function rollThreeCoins(): { faces: CoinFace[]; yaoValue: YaoValue } {
    const vals = [
      Math.random() < 0.5 ? 2 : 3,
      Math.random() < 0.5 ? 2 : 3,
      Math.random() < 0.5 ? 2 : 3,
    ]
    const sum = vals.reduce((a, b) => a + b, 0) as YaoValue // 6/7/8/9
    return {
      faces: vals.map((v) => (v === 3 ? "正" : "反")) as CoinFace[],
      yaoValue: sum,
    }
  }

  // ── 开始摇 ────────────────────────────────────────────────────────────────
  function startShake() {
    if (shaking || isDone) return
    const result = rollThreeCoins()
    setPendingResult(result)
    setShaking(true)
    // 每 80ms 随机切换显示面，模拟铜钱翻滚
    shakeIntervalRef.current = setInterval(() => {
      setDisplayFaces([
        Math.random() < 0.5 ? "正" : "反",
        Math.random() < 0.5 ? "正" : "反",
        Math.random() < 0.5 ? "正" : "反",
      ])
    }, 80)
  }

  // ── 停止 ──────────────────────────────────────────────────────────────────
  function stopShake() {
    if (!shaking || !pendingResult) return
    if (shakeIntervalRef.current) {
      clearInterval(shakeIntervalRef.current)
      shakeIntervalRef.current = null
    }
    setShaking(false)
    setDisplayFaces(pendingResult.faces)
    setYaos((prev: YaoValue[]) => [...prev, pendingResult.yaoValue])
    setPendingResult(null)
  }

  // ── 重置 ──────────────────────────────────────────────────────────────────
  function reset() {
    if (shakeIntervalRef.current) {
      clearInterval(shakeIntervalRef.current)
      shakeIntervalRef.current = null
    }
    setYaos([])
    setShaking(false)
    setPendingResult(null)
    setDisplayFaces(["正", "正", "正"])
  }

  // ── 清理定时器 ─────────────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      if (shakeIntervalRef.current) clearInterval(shakeIntervalRef.current)
    }
  }, [])

  // ── 提交起卦 ───────────────────────────────────────────────────────────────
  const mutation = useMutation({
    mutationFn: (lines: YaoValue[]) => {
      const v = getValues()
      return axios
        .post(
          `${API_BASE}/api/v1/liuyao/cast/manual`,
          {
            lines,
            caster_name: v.caster_name || undefined,
            caster_gender: v.caster_gender || undefined,
            question: v.question || undefined,
          },
          { headers: authHeaders() },
        )
        .then((r) => r.data)
    },
    onSuccess: onResult,
  })

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <Stack gap={4}>
      <Text color="gray.600" fontSize="sm">
        模拟三枚铜钱摇卦：正面=3（阳）反面=2（阴），三枚之和决定本爻。共需摇
        <Text as="span" fontWeight="semibold">
          &nbsp;六次&nbsp;
        </Text>
        依次揭示六爻，由第一爻（下）至第六爻（上）。
      </Text>

      {/* ── 用户信息 ─────────────────────────────────────────────────────── */}
      <Grid templateColumns={{ base: "1fr", md: "1fr 1fr 2fr" }} gap={3}>
        <Box>
          <Text fontSize="sm" mb={1} color="gray.600">
            姓名（选填）
          </Text>
          <Input placeholder="请输入姓名" {...register("caster_name")} />
        </Box>
        <Box>
          <Text fontSize="sm" mb={1} color="gray.600">
            性别（选填）
          </Text>
          <NativeSelect.Root>
            <NativeSelect.Field {...register("caster_gender")}>
              <option value="">不填</option>
              <option value="男">男</option>
              <option value="女">女</option>
              <option value="其他">其他</option>
            </NativeSelect.Field>
          </NativeSelect.Root>
        </Box>
        <Box>
          <Text fontSize="sm" mb={1} color="gray.600">
            占事（选填）
          </Text>
          <Input
            placeholder="如：今日出行、感情运势…"
            {...register("question")}
          />
        </Box>
      </Grid>

      {/* ── 进度提示 ─────────────────────────────────────────────────────── */}
      <Flex align="center" gap={2}>
        <Text fontSize="sm" fontWeight="semibold" color="gray.700">
          进度：
        </Text>
        {[1, 2, 3, 4, 5, 6].map((n) => (
          <Box
            key={n}
            w="28px"
            h="28px"
            borderRadius="full"
            border="2px solid"
            borderColor={
              n <= yaos.length
                ? "teal.400"
                : n === yaos.length + 1
                  ? "orange.400"
                  : "gray.200"
            }
            bg={
              n <= yaos.length
                ? "teal.50"
                : n === yaos.length + 1
                  ? "orange.50"
                  : "transparent"
            }
            display="flex"
            alignItems="center"
            justifyContent="center"
            fontSize="xs"
            fontWeight="bold"
            color={
              n <= yaos.length
                ? "teal.600"
                : n === yaos.length + 1
                  ? "orange.500"
                  : "gray.300"
            }
          >
            {n <= yaos.length ? "✓" : n}
          </Box>
        ))}
        {isDone && (
          <Text fontSize="sm" color="teal.500" fontWeight="semibold" ml={1}>
            六爻已定！
          </Text>
        )}
      </Flex>

      {/* ── 铜钱摇动区域 ──────────────────────────────────────────────────── */}
      {!isDone && (
        <Box
          p={5}
          borderWidth={1}
          borderRadius="xl"
          bg="orange.50"
          borderColor="orange.200"
          textAlign="center"
        >
          <Text fontSize="xs" color="gray.500" mb={3}>
            第 {currentYaoIdx + 1} 爻
            {shaking ? " — 摇动中，点击停止揭示本爻" : " — 点击开始摇铜钱"}
          </Text>

          {/* 三枚铜钱 */}
          <Flex justify="center" gap={5} mb={4}>
            {displayFaces.map((face: CoinFace, i: number) => {
              const isYang = face === "正"
              return (
                <div
                  key={i}
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: "50%",
                    backgroundColor: isYang ? "#ECC94B" : "#CBD5E0",
                    color: isYang ? "#744210" : "#4A5568",
                    boxShadow: shaking
                      ? "0 4px 18px rgba(0,0,0,0.28)"
                      : "0 2px 8px rgba(0,0,0,0.15)",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    userSelect: "none",
                    cursor: "default",
                    animation: shaking
                      ? `coinShake 0.35s infinite ${i * 0.07}s`
                      : "none",
                    transition: "background-color 0.08s",
                  }}
                >
                  <span style={{ fontSize: 22, lineHeight: 1 }}>{face}</span>
                  <span style={{ fontSize: 9, marginTop: 2, opacity: 0.7 }}>
                    {face === "正" ? "3·阳" : "2·阴"}
                  </span>
                </div>
              )
            })}
          </Flex>

          {/* 本次爻值提示（停止后显示） */}
          {!shaking && yaos.length > 0 && (() => {
            const lastVal = yaos[yaos.length - 1]
            const isYang = lastVal === 7 || lastVal === 9
            const isChanging = lastVal === 6 || lastVal === 9
            const labels: Record<number, string> = {
              6: "老阴（变爻）",
              7: "少阳",
              8: "少阴",
              9: "老阳（变爻）",
            }
            return (
              <Text fontSize="xs" color={isChanging ? "orange.500" : "gray.600"} mb={3} fontWeight="semibold">
                第 {yaos.length} 爻：{isYang ? "阳爻" : "阴爻"} — {labels[lastVal]}（{lastVal}）
                {isChanging && "  ○ 动爻"}
              </Text>
            )
          })()}

          {/* 操作按钮 */}
          <Flex justify="center" gap={3}>
            <Button
              colorScheme="orange"
              onClick={startShake}
              disabled={shaking}
              size="md"
            >
              🪙 开始摇
            </Button>
            <Button
              colorScheme="teal"
              onClick={stopShake}
              disabled={!shaking}
              size="md"
            >
              ✋ 停止
            </Button>
          </Flex>
        </Box>
      )}

      {/* ── 爻线预览（由上至下：第六爻→第一爻） ─────────────────────────── */}
      <Box
        p={4}
        borderWidth={1}
        borderRadius="lg"
        bg="gray.50"
        borderColor="gray.200"
      >
        <Text fontSize="xs" color="gray.400" mb={2} textAlign="center">
          卦象预览（由上至下：第六爻 → 第一爻）
        </Text>
        <Stack gap={2} align="center">
          {[5, 4, 3, 2, 1, 0].map((idx) => {
            const val = yaos[idx]
            const isRevealed = val !== undefined
            const isYang = val === 7 || val === 9
            const isChanging = val === 6 || val === 9
            const lineColor = isChanging
              ? "#ED8936" // orange
              : isRevealed
                ? "#2D3748" // gray.800
                : "#E2E8F0" // gray.200 placeholder

            return (
              <Flex
                key={idx}
                align="center"
                gap={3}
                h="24px"
                style={
                  isRevealed
                    ? { animation: "yaoReveal 0.4s ease-out" }
                    : {}
                }
              >
                <Text
                  fontSize="10px"
                  w="32px"
                  textAlign="right"
                  color={isRevealed ? "gray.600" : "gray.300"}
                  fontWeight={isRevealed ? "semibold" : "normal"}
                >
                  {idx + 1}爻
                </Text>
                {/* 爻线线 */}
                {!isRevealed || isYang ? (
                  <Box
                    h="5px"
                    w="80px"
                    bg={lineColor}
                    borderRadius="sm"
                    opacity={isRevealed ? 1 : 0.35}
                  />
                ) : (
                  <Flex gap="8px">
                    <Box
                      h="5px"
                      w="34px"
                      bg={lineColor}
                      borderRadius="sm"
                    />
                    <Box
                      h="5px"
                      w="34px"
                      bg={lineColor}
                      borderRadius="sm"
                    />
                  </Flex>
                )}
                {isChanging && (
                  <Text fontSize="xs" color="orange.500" ml={1}>
                    ○
                  </Text>
                )}
                {isRevealed && (
                  <Text fontSize="9px" color="gray.400" ml={1}>
                    ({val})
                  </Text>
                )}
              </Flex>
            )
          })}
        </Stack>
      </Box>

      {/* ── 六爻确定后的操作 ──────────────────────────────────────────────── */}
      {isDone && (
        <Flex gap={3} flexWrap="wrap">
          <Button
            colorScheme="teal"
            size="lg"
            onClick={() => mutation.mutate(yaos)}
            loading={mutation.isPending}
          >
            ✨ 提交起卦
          </Button>
          <Button variant="outline" size="lg" onClick={reset} disabled={mutation.isPending}>
            🔄 重新摇卦
          </Button>
        </Flex>
      )}

      {mutation.isError && (
        <Text color="red.500" fontSize="sm">
          起卦失败，请稍后重试。
        </Text>
      )}
    </Stack>
  )
}
