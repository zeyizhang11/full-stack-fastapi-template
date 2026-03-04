import {
  Box,
  Container,
  Flex,
  Heading,
  Separator,
  Tabs,
  Text,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Link as RouterLink, createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { CoinCastForm } from "@/components/LiuYao/CoinCastForm"
import { isLoggedIn } from "@/hooks/useAuth"

import { fetchHistory, fetchHexagrams } from "@/components/LiuYao/api"
import { HexagramDisplay } from "@/components/LiuYao/HexagramDisplay"
import { HistoryList } from "@/components/LiuYao/HistoryList"
import { ManualForm } from "@/components/LiuYao/ManualForm"
import { NumbersForm } from "@/components/LiuYao/NumbersForm"
import { TimeForm } from "@/components/LiuYao/TimeForm"
import type { HexagramReading } from "@/components/LiuYao/types"

//  Route 

export const Route = createFileRoute("/liuyao")({
  component: LiuYaoPage,
})

function LiuYaoPage() {
  const loggedIn = isLoggedIn()
  const queryClient = useQueryClient()
  const [currentReading, setCurrentReading] = useState<HexagramReading | null>(null)

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

  const handleResult = (r: HexagramReading) => {
    setCurrentReading(r)
    if (loggedIn) queryClient.invalidateQueries({ queryKey: ["liuyao-history"] })
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  return (
    <Container maxW="3xl" py={8}>
      {/* Header */}
      <Flex justify="space-between" align="center" mb={2}>
        <Heading size="xl"> 六爻排盘</Heading>
        <Flex gap={3} align="center">
          {loggedIn ? (
            <RouterLink to="/"><Button variant="outline" size="sm">返回主页</Button></RouterLink>
          ) : (
            <>
              <RouterLink to="/login"><Button variant="outline" size="sm">登录</Button></RouterLink>
              <RouterLink to="/signup"><Button size="sm">注册</Button></RouterLink>
            </>
          )}
        </Flex>
      </Flex>
      <Text color="gray.600" mb={6} fontSize="sm">
        支持四种起卦方式，无需登录即可起卦，登录后可保存历史记录。
      </Text>

      {/* Result */}
      {currentReading && (
        <HexagramDisplay reading={currentReading} hexagrams={hexagrams} />
      )}

      {/* Casting Tabs */}
      <Box mt={6} borderWidth={1} borderRadius="lg" p={5}>
        <Tabs.Root defaultValue="coin" variant="enclosed">
          <Tabs.List mb={4}>
            <Tabs.Trigger value="coin"> 三铜钱法</Tabs.Trigger>
            <Tabs.Trigger value="time"> 时间起卦</Tabs.Trigger>
            <Tabs.Trigger value="numbers"> 报数起卦</Tabs.Trigger>
            <Tabs.Trigger value="manual"> 手动填爻</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="coin">
            <CoinCastForm onResult={handleResult} />
          </Tabs.Content>
          <Tabs.Content value="time">
            <TimeForm onResult={handleResult} />
          </Tabs.Content>
          <Tabs.Content value="numbers">
            <NumbersForm onResult={handleResult} />
          </Tabs.Content>
          <Tabs.Content value="manual">
            <ManualForm onResult={handleResult} />
          </Tabs.Content>
        </Tabs.Root>
      </Box>

      {/* History */}
      {loggedIn && (
        <>
          <Separator my={8} />
          <HistoryList history={history ?? []} hexagrams={hexagrams} />
        </>
      )}
    </Container>
  )
}
