import {
  Badge,
  Box,
  Container,
  Flex,
  Heading,
  Input,
  Separator,
  Stack,
  Text,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink, createFileRoute } from "@tanstack/react-router"
import axios from "axios"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { isLoggedIn } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"

const API_BASE = import.meta.env.VITE_API_URL ?? ""

interface HexagramReading {
  id: string
  reading_number: string
  question: string | null
  lines: number[]
  hexagram_number: number
  changed_hexagram_number: number | null
  created_at: string
  user_id: string | null
}

interface HexagramInfo {
  zh: string
  pinyin: string
  en: string
  judgment: string
}

function getToken(): string | null {
  return localStorage.getItem("access_token")
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function castHexagram(question?: string): Promise<HexagramReading> {
  const { data } = await axios.post(
    `${API_BASE}/api/v1/liuyao/cast`,
    { question: question || null },
    { headers: authHeaders() },
  )
  return data
}

async function fetchHistory(): Promise<HexagramReading[]> {
  const { data } = await axios.get(`${API_BASE}/api/v1/liuyao/`, {
    headers: authHeaders(),
  })
  return data.data
}

async function fetchHexagrams(): Promise<Record<string, HexagramInfo>> {
  const { data } = await axios.get(`${API_BASE}/api/v1/liuyao/hexagrams`)
  return data
}

async function lookupReading(readingNumber: string): Promise<HexagramReading> {
  const { data } = await axios.get(
    `${API_BASE}/api/v1/liuyao/${encodeURIComponent(readingNumber)}`,
    { headers: authHeaders() },
  )
  return data
}

async function deleteReading(readingId: string): Promise<void> {
  await axios.delete(`${API_BASE}/api/v1/liuyao/${readingId}`, {
    headers: authHeaders(),
  })
}

export const Route = createFileRoute("/liuyao")({
  component: LiuYaoPage,
})

/** Render a single yao line (solid = yang, broken = yin, changing = orange) */
function YaoLine({ value, index }: { value: number; index: number }) {
  const isYang = value === 7 || value === 9
  const isChanging = value === 6 || value === 9
  const color = isChanging ? "orange.500" : isYang ? "gray.800" : "gray.800"
  return (
    <Flex align="center" gap={2} my={1}>
      <Text fontSize="xs" color="gray.500" w={4}>
        {index + 1}
      </Text>
      {isYang ? (
        <Box h="4px" w="80px" bg={color} borderRadius="sm" />
      ) : (
        <Flex gap={2}>
          <Box h="4px" w="36px" bg={color} borderRadius="sm" />
          <Box h="4px" w="36px" bg={color} borderRadius="sm" />
        </Flex>
      )}
      {isChanging && (
        <Text fontSize="xs" color="orange.500">
          变
        </Text>
      )}
    </Flex>
  )
}

function HexagramDisplay({
  reading,
  hexagrams,
}: {
  reading: HexagramReading
  hexagrams: Record<string, HexagramInfo> | undefined
}) {
  const base = hexagrams?.[String(reading.hexagram_number)]
  const changed =
    reading.changed_hexagram_number != null
      ? hexagrams?.[String(reading.changed_hexagram_number)]
      : null

  return (
    <Box
      borderWidth={1}
      borderRadius="md"
      p={4}
      mt={4}
      bg="gray.subtle"
    >
      <Text fontSize="xs" color="gray.500" mb={1}>
        编号：{reading.reading_number}
      </Text>
      {reading.question && (
        <Text fontWeight="semibold" mb={2}>
          问：{reading.question}
        </Text>
      )}
      <Flex gap={8} flexWrap="wrap">
        <Box>
          <Text fontSize="sm" fontWeight="bold" mb={1}>
            本卦
          </Text>
          {/* Lines are shown bottom (index 0) to top (index 5) */}
          {[...reading.lines].reverse().map((v, i) => (
            <YaoLine key={i} value={v} index={5 - i} />
          ))}
          {base && (
            <Box mt={2}>
              <Text fontSize="lg" fontWeight="bold">
                {base.zh}（{base.pinyin}）
              </Text>
              <Text fontSize="sm" color="gray.600">
                {base.en}
              </Text>
              <Text fontSize="sm" mt={1} color="gray.700">
                {base.judgment}
              </Text>
            </Box>
          )}
        </Box>
        {changed && reading.changed_hexagram_number != null && (
          <Box>
            <Text fontSize="sm" fontWeight="bold" mb={1}>
              变卦
            </Text>
            <Badge colorScheme="orange" mb={2}>
              → {changed.zh}
            </Badge>
            <Text fontSize="lg" fontWeight="bold">
              {changed.zh}（{changed.pinyin}）
            </Text>
            <Text fontSize="sm" color="gray.600">
              {changed.en}
            </Text>
            <Text fontSize="sm" mt={1} color="gray.700">
              {changed.judgment}
            </Text>
          </Box>
        )}
      </Flex>
    </Box>
  )
}

function LiuYaoPage() {
  const loggedIn = isLoggedIn()
  const queryClient = useQueryClient()
  const [currentReading, setCurrentReading] = useState<HexagramReading | null>(
    null,
  )
  const [lookupNumber, setLookupNumber] = useState("")
  const [lookupResult, setLookupResult] = useState<HexagramReading | null>(null)
  const [lookupError, setLookupError] = useState<string | null>(null)

  const { register, handleSubmit } = useForm<{ question: string }>()

  const { data: hexagrams } = useQuery({
    queryKey: ["hexagrams"],
    queryFn: fetchHexagrams,
    staleTime: Infinity,
  })

  const { data: history } = useQuery({
    queryKey: ["liuyao-history"],
    queryFn: fetchHistory,
    enabled: loggedIn,
  })

  const castMutation = useMutation({
    mutationFn: (question: string) => castHexagram(question),
    onSuccess: (data) => {
      setCurrentReading(data)
      if (loggedIn) {
        queryClient.invalidateQueries({ queryKey: ["liuyao-history"] })
      }
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteReading(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["liuyao-history"] })
    },
  })

  const onCast = handleSubmit((values) => {
    castMutation.mutate(values.question)
  })

  const onLookup = async () => {
    setLookupError(null)
    setLookupResult(null)
    try {
      const r = await lookupReading(lookupNumber.trim())
      setLookupResult(r)
    } catch {
      setLookupError("未找到该编号的卦象，请检查后重试。")
    }
  }

  return (
    <Container maxW="2xl" py={8}>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="xl">☯ 六爻排盘</Heading>
        <Flex gap={3} align="center">
          {loggedIn ? (
            <RouterLink to="/">
              <Button variant="outline" size="sm">
                返回主页
              </Button>
            </RouterLink>
          ) : (
            <>
              <RouterLink to="/login">
                <Button variant="outline" size="sm">
                  登录
                </Button>
              </RouterLink>
              <RouterLink to="/signup">
                <Button size="sm">注册</Button>
              </RouterLink>
            </>
          )}
        </Flex>
      </Flex>

      <Text color="gray.600" mb={6}>
        通过三枚铜钱法起卦，探索六十四卦的智慧。无需登录即可起卦，登录后可保存历史记录。
      </Text>

      {/* Cast form */}
      <Box as="form" onSubmit={onCast}>
        <Stack gap={3}>
          <Input
            placeholder="请输入您的问题（选填）"
            {...register("question")}
            maxLength={200}
          />
          <Button
            type="submit"
            loading={castMutation.isPending}
            colorScheme="teal"
          >
            起卦
          </Button>
        </Stack>
      </Box>

      {castMutation.isError && (
        <Text color="red.500" mt={2}>
          起卦失败，请稍后重试。
        </Text>
      )}

      {currentReading && (
        <HexagramDisplay reading={currentReading} hexagrams={hexagrams} />
      )}

      <Separator my={8} />

      {/* Lookup by number */}
      <Box>
        <Heading size="md" mb={3}>
          查询卦象
        </Heading>
        <Flex gap={2}>
          <Input
            placeholder="输入编号，如 LY-20260225-A1B2"
            value={lookupNumber}
            onChange={(e) => setLookupNumber(e.target.value)}
          />
          <Button onClick={onLookup} variant="outline">
            查询
          </Button>
        </Flex>
        {lookupError && (
          <Text color="red.500" mt={2}>
            {lookupError}
          </Text>
        )}
        {lookupResult && (
          <HexagramDisplay reading={lookupResult} hexagrams={hexagrams} />
        )}
      </Box>

      {/* History (logged-in users only) */}
      {loggedIn && (
        <>
          <Separator my={8} />
          <Box>
            <Heading size="md" mb={3}>
              我的历史记录
            </Heading>
            {!history || history.length === 0 ? (
              <Text color="gray.500">暂无记录</Text>
            ) : (
              <Stack gap={3}>
                {history.map((r) => (
                  <Box
                    key={r.id}
                    borderWidth={1}
                    borderRadius="md"
                    p={3}
                    bg="gray.subtle"
                  >
                    <Flex justify="space-between" align="start">
                      <Box>
                        <Text fontSize="xs" color="gray.500">
                          {r.reading_number} · {r.created_at.slice(0, 10)}
                        </Text>
                        {r.question && (
                          <Text fontSize="sm" mt={1}>
                            {r.question}
                          </Text>
                        )}
                        <Text fontSize="sm" mt={1} fontWeight="semibold">
                          {hexagrams?.[String(r.hexagram_number)]?.zh ?? `卦${r.hexagram_number}`}
                          {r.changed_hexagram_number != null &&
                            ` → ${hexagrams?.[String(r.changed_hexagram_number)]?.zh ?? `卦${r.changed_hexagram_number}`}`}
                        </Text>
                      </Box>
                      <Button
                        size="xs"
                        colorScheme="red"
                        variant="ghost"
                        onClick={() => deleteMutation.mutate(r.id)}
                        loading={deleteMutation.isPending}
                      >
                        删除
                      </Button>
                    </Flex>
                  </Box>
                ))}
              </Stack>
            )}
          </Box>
        </>
      )}
    </Container>
  )
}
