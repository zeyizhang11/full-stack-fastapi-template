import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  Heading,
  Input,
  Separator,
  Spinner,
  Stack,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink, createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { FiBookOpen, FiLogIn, FiUser, FiZap } from "react-icons/fi"

import { OpenAPI } from "@/client"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/liuyao")({
  component: LiuYaoPage,
})

// ---- Types ----
interface HexagramReadingPublic {
  id: string
  reading_number: string
  question: string | null
  lines: number[]
  hexagram_number: number
  hexagram_name: string
  hexagram_english: string
  hexagram_judgment: string
  changed_hexagram_number: number | null
  changed_hexagram_name: string | null
  changing_lines: number[]
  created_at: string
  user_id: string | null
}

interface HexagramReadingsPublic {
  data: HexagramReadingPublic[]
  count: number
}

// ---- API helpers ----
async function castHexagram(question?: string): Promise<HexagramReadingPublic> {
  const token = localStorage.getItem("access_token")
  const res = await fetch(`${OpenAPI.BASE}/api/v1/liuyao/cast`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ question: question || null }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function fetchMyReadings(): Promise<HexagramReadingsPublic> {
  const token = localStorage.getItem("access_token")
  const res = await fetch(`${OpenAPI.BASE}/api/v1/liuyao/?limit=10`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function deleteReading(id: string): Promise<void> {
  const token = localStorage.getItem("access_token")
  const res = await fetch(`${OpenAPI.BASE}/api/v1/liuyao/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(await res.text())
}

// ---- Hexagram visual rendering ----
const LINE_YANG = "————————————"
const LINE_YIN_L = "—————"
const LINE_YIN_R = "—————"

function HexagramLine({
  value,
  position,
  isChanging,
}: {
  value: number
  position: number
  isChanging: boolean
}) {
  const isYang = value === 7 || value === 9

  return (
    <Flex align="center" gap={2} h="24px" w="full" justify="center">
      <Text fontSize="xs" color="gray.400" w="4" textAlign="right">
        {position}
      </Text>
      {isYang ? (
        <Text
          fontFamily="monospace"
          fontSize="xl"
          letterSpacing="2px"
          color={isChanging ? "orange.400" : "inherit"}
          fontWeight="bold"
        >
          {LINE_YANG}
        </Text>
      ) : (
        <Flex gap={3} align="center">
          <Text
            fontFamily="monospace"
            fontSize="xl"
            color={isChanging ? "orange.400" : "inherit"}
            fontWeight="bold"
          >
            {LINE_YIN_L}
          </Text>
          <Text
            fontFamily="monospace"
            fontSize="xl"
            color={isChanging ? "orange.400" : "inherit"}
            fontWeight="bold"
          >
            {LINE_YIN_R}
          </Text>
        </Flex>
      )}
      {isChanging && (
        <Text fontSize="xs" color="orange.400" fontWeight="bold">
          ○
        </Text>
      )}
    </Flex>
  )
}

function HexagramDisplay({
  reading,
  compact = false,
}: {
  reading: HexagramReadingPublic
  compact?: boolean
}) {
  const changingSet = new Set(reading.changing_lines)
  const lines = reading.lines ?? []

  return (
    <Box>
      {/* Lines from top (6) to bottom (1) */}
      <VStack gap={compact ? 0 : 1} mb={compact ? 2 : 4}>
        {[...lines].reverse().map((val, idx) => {
          const pos = lines.length - idx
          return (
            <HexagramLine
              key={pos}
              value={val}
              position={pos}
              isChanging={changingSet.has(pos)}
            />
          )
        })}
      </VStack>
      <Box textAlign="center">
        <Text fontSize={compact ? "md" : "2xl"} fontWeight="bold">
          第{reading.hexagram_number}卦 · {reading.hexagram_name}
        </Text>
        <Text fontSize={compact ? "xs" : "sm"} color="gray.500">
          {reading.hexagram_english}
        </Text>
        {!compact && (
          <Text fontSize="sm" color="teal.600" mt={2} fontStyle="italic">
            《彖》{reading.hexagram_judgment}
          </Text>
        )}
        {reading.changed_hexagram_name && (
          <Badge colorPalette="orange" mt={2}>
            变卦：{reading.changed_hexagram_name}
          </Badge>
        )}
      </Box>
    </Box>
  )
}

// ---- Cast form ----
function CastForm({
  onResult,
}: {
  onResult: (r: HexagramReadingPublic) => void
}) {
  const [question, setQuestion] = useState("")

  const mutation = useMutation({
    mutationFn: () => castHexagram(question),
    onSuccess: (data) => {
      onResult(data)
      setQuestion("")
    },
  })

  return (
    <VStack gap={4} align="stretch">
      <Textarea
        placeholder="请输入您的问题（可选）…"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        rows={3}
        resize="none"
      />
      <Button
        colorPalette="teal"
        size="lg"
        onClick={() => mutation.mutate()}
        loading={mutation.isPending}
        loadingText="起卦中…"
      >
        <FiZap />
        起卦
      </Button>
      {mutation.isError && (
        <Text color="red.500" fontSize="sm">
          起卦失败，请稍后重试
        </Text>
      )}
    </VStack>
  )
}

// ---- History list ----
function ReadingHistoryItem({
  reading,
  onDelete,
}: {
  reading: HexagramReadingPublic
  onDelete?: (id: string) => void
}) {
  return (
    <Box
      borderWidth="1px"
      borderRadius="md"
      p={4}
      _hover={{ bg: "gray.subtle" }}
    >
      <Flex justify="space-between" align="start">
        <Box flex="1">
          <Flex gap={2} align="center" mb={1}>
            <Text fontSize="xs" color="gray.500" fontFamily="mono">
              {reading.reading_number}
            </Text>
            <Text fontSize="xs" color="gray.400">
              {new Date(reading.created_at).toLocaleString("zh-CN")}
            </Text>
          </Flex>
          {reading.question && (
            <Text fontSize="sm" mb={2} color="gray.700">
              问：{reading.question}
            </Text>
          )}
          <Flex gap={2} align="center">
            <Text fontWeight="semibold" fontSize="sm">
              第{reading.hexagram_number}卦 · {reading.hexagram_name}
            </Text>
            {reading.changed_hexagram_name && (
              <Badge colorPalette="orange" size="sm">
                变→{reading.changed_hexagram_name}
              </Badge>
            )}
          </Flex>
        </Box>
        {onDelete && (
          <Button
            size="xs"
            variant="ghost"
            colorPalette="red"
            onClick={() => onDelete(reading.id)}
            aria-label="删除"
          >
            删除
          </Button>
        )}
      </Flex>
    </Box>
  )
}

function UserReadingHistory() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ["liuyao-readings"],
    queryFn: fetchMyReadings,
    enabled: isLoggedIn(),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteReading,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["liuyao-readings"] })
    },
  })

  if (!isLoggedIn()) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="md" textAlign="center">
        <Text color="gray.500" fontSize="sm">
          登录后可查看历史排盘记录
        </Text>
      </Box>
    )
  }

  if (isLoading) return <Spinner />

  const readings = data?.data ?? []

  if (readings.length === 0) {
    return (
      <Box p={4} borderWidth="1px" borderRadius="md" textAlign="center">
        <Text color="gray.500" fontSize="sm">
          暂无排盘记录，点击"起卦"开始第一次排盘
        </Text>
      </Box>
    )
  }

  return (
    <VStack gap={3} align="stretch">
      {readings.map((r) => (
        <ReadingHistoryItem
          key={r.id}
          reading={r}
          onDelete={(id) => deleteMutation.mutate(id)}
        />
      ))}
    </VStack>
  )
}

// ---- Main page ----
function LiuYaoPage() {
  const { user, logout } = useAuth()
  const queryClient = useQueryClient()
  const [currentReading, setCurrentReading] =
    useState<HexagramReadingPublic | null>(null)
  const [lookupNumber, setLookupNumber] = useState("")
  const [lookupResult, setLookupResult] =
    useState<HexagramReadingPublic | null>(null)
  const [lookupError, setLookupError] = useState("")

  const handleResult = (reading: HexagramReadingPublic) => {
    setCurrentReading(reading)
    if (isLoggedIn()) {
      queryClient.invalidateQueries({ queryKey: ["liuyao-readings"] })
    }
  }

  const handleLookup = async () => {
    if (!lookupNumber.trim()) return
    setLookupError("")
    setLookupResult(null)
    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch(
        `${OpenAPI.BASE}/api/v1/liuyao/${encodeURIComponent(lookupNumber.trim())}`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        },
      )
      if (!res.ok) {
        setLookupError(res.status === 404 ? "未找到该排盘记录" : "查询失败")
        return
      }
      setLookupResult(await res.json())
    } catch {
      setLookupError("网络错误，请稍后重试")
    }
  }

  return (
    <Box minH="100vh" bg="gray.50">
      {/* Header */}
      <Box
        bg="white"
        borderBottomWidth="1px"
        borderColor="gray.200"
        px={6}
        py={3}
      >
        <Flex maxW="6xl" mx="auto" justify="space-between" align="center">
          <Flex align="center" gap={2}>
            <Text fontSize="xl" fontWeight="bold">
              ☰ 六爻排盘
            </Text>
            {user && (
              <Badge colorPalette="teal" variant="subtle">
                {user.full_name || user.email}
              </Badge>
            )}
          </Flex>
          <Flex gap={2}>
            {isLoggedIn() ? (
              <>
                <RouterLink to="/">
                  <Button size="sm" variant="ghost">
                    <FiUser />
                    控制台
                  </Button>
                </RouterLink>
                <Button size="sm" variant="ghost" onClick={logout}>
                  退出
                </Button>
              </>
            ) : (
              <>
                <RouterLink to="/login">
                  <Button size="sm" variant="ghost">
                    <FiLogIn />
                    登录
                  </Button>
                </RouterLink>
                <RouterLink to="/signup">
                  <Button size="sm" colorPalette="teal">
                    注册
                  </Button>
                </RouterLink>
              </>
            )}
          </Flex>
        </Flex>
      </Box>

      {/* Body */}
      <Container maxW="6xl" py={8}>
        <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={8}>
          {/* Left: Cast + Result */}
          <Stack gap={6}>
            {/* Cast card */}
            <Box bg="white" borderRadius="xl" p={6} shadow="sm">
              <Heading size="md" mb={4}>
                起卦
              </Heading>
              <Text fontSize="sm" color="gray.500" mb={4}>
                以三枚铜钱摇六次，排出六爻卦象。登录后排盘将与您的账号关联。
              </Text>
              <CastForm onResult={handleResult} />
            </Box>

            {/* Current result card */}
            {currentReading && (
              <Box bg="white" borderRadius="xl" p={6} shadow="sm">
                <Flex justify="space-between" align="center" mb={4}>
                  <Heading size="md">本次卦象</Heading>
                  <Text fontSize="xs" color="gray.400" fontFamily="mono">
                    {currentReading.reading_number}
                  </Text>
                </Flex>
                {currentReading.question && (
                  <Text
                    fontSize="sm"
                    color="gray.600"
                    mb={4}
                    fontStyle="italic"
                  >
                    问：{currentReading.question}
                  </Text>
                )}
                <HexagramDisplay reading={currentReading} />
              </Box>
            )}

            {/* Lookup by number */}
            <Box bg="white" borderRadius="xl" p={6} shadow="sm">
              <Heading size="md" mb={4}>
                <FiBookOpen style={{ display: "inline", marginRight: 8 }} />
                按编号查询
              </Heading>
              <Flex gap={2}>
                <Input
                  placeholder="如 LY-20260225-A1B2"
                  value={lookupNumber}
                  onChange={(e) => setLookupNumber(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleLookup()}
                  flex="1"
                />
                <Button
                  onClick={handleLookup}
                  colorPalette="teal"
                  variant="outline"
                >
                  查询
                </Button>
              </Flex>
              {lookupError && (
                <Text color="red.500" fontSize="sm" mt={2}>
                  {lookupError}
                </Text>
              )}
              {lookupResult && (
                <Box mt={4}>
                  <Separator mb={4} />
                  <HexagramDisplay reading={lookupResult} />
                </Box>
              )}
            </Box>
          </Stack>

          {/* Right: History */}
          <Box>
            <Box bg="white" borderRadius="xl" p={6} shadow="sm">
              <Heading size="md" mb={4}>
                历史排盘
              </Heading>
              <UserReadingHistory />
            </Box>
          </Box>
        </Grid>
      </Container>
    </Box>
  )
}
