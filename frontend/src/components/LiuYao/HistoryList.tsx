import { Badge, Box, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { Button } from "@/components/ui/button"
import { deleteReading } from "./api"
import type { HexagramInfo, HexagramReading } from "./types"

interface HistoryListProps {
  history: HexagramReading[]
  hexagrams: Record<string, HexagramInfo> | undefined
}

const CAST_METHOD_SHORT: Record<string, string> = {
  coin: "三铜钱",
  time: "时间",
  numbers: "报数",
  manual: "手动",
}

export function HistoryList({ history, hexagrams }: HistoryListProps) {
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteReading(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["liuyao-history"] }),
  })

  return (
    <Box>
      <Heading size="md" mb={3}>我的历史记录</Heading>
      {history.length === 0 ? (
        <Text color="gray.500">暂无记录</Text>
      ) : (
        <Stack gap={3}>
          {history.map((r) => (
            <Box key={r.id} borderWidth={1} borderRadius="md" p={3} bg="gray.subtle">
              <Flex justify="space-between" align="start">
                <Box>
                  <Flex gap={2} align="center" flexWrap="wrap">
                    <Text fontSize="xs" color="gray.500">
                      {r.reading_number} · {r.created_at.slice(0, 10)}
                    </Text>
                    <Badge fontSize="xs" colorScheme="purple">
                      {CAST_METHOD_SHORT[r.cast_method] ?? r.cast_method}
                    </Badge>
                    {r.caster_name && <Badge fontSize="xs">{r.caster_name}</Badge>}
                  </Flex>
                  {r.question && (
                    <Text fontSize="sm" mt={1}>{r.question}</Text>
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
  )
}
