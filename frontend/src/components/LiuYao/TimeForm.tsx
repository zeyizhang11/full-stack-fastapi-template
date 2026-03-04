import { Box, Grid, Input, Stack, Text } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import axios from "axios"
import { useForm } from "react-hook-form"

import { Button } from "@/components/ui/button"
import { API_BASE, authHeaders } from "./constants"
import type { HexagramReading, TimeFormValues } from "./types"
import { UserInfoFields } from "./UserInfoFields"

interface TimeFormProps {
  onResult: (r: HexagramReading) => void
}

export function TimeForm({ onResult }: TimeFormProps) {
  const now = new Date()
  const { register, handleSubmit } = useForm<TimeFormValues>({
    defaultValues: {
      year: now.getFullYear(),
      month: now.getMonth() + 1,
      day: now.getDate(),
      hour: now.getHours(),
    },
  })

  const mutation = useMutation({
    mutationFn: (v: TimeFormValues) =>
      axios
        .post(
          `${API_BASE}/api/v1/liuyao/cast/time`,
          {
            ...v,
            year: Number(v.year),
            month: Number(v.month),
            day: Number(v.day),
            hour: Number(v.hour),
          },
          { headers: authHeaders() },
        )
        .then((r) => r.data),
    onSuccess: onResult,
  })

  const fieldLabels: Record<string, string> = {
    year: "年",
    month: "月",
    day: "日",
    hour: "时（0-23）",
  }

  return (
    <Box as="form" onSubmit={handleSubmit((v) => mutation.mutate(v))}>
      <Stack gap={4}>
        <Text color="gray.600" fontSize="sm">
          依邵雍先天法：上卦＝（年支＋农历月＋农历日）mod 8，下卦＝（…＋时支）mod 8，动爻＝（…）mod 6。
          <br />
          输入<Text as="span" fontWeight="semibold"> 公历</Text>日期与时辰，系统自动换算农历及年支后起卦。
        </Text>
        <Grid templateColumns={{ base: "1fr 1fr", md: "1fr 1fr 1fr 1fr" }} gap={3}>
          {(["year", "month", "day", "hour"] as const).map((f) => (
            <Box key={f}>
              <Text fontSize="sm" mb={1} color="gray.600">{fieldLabels[f]}</Text>
              <Input type="number" {...register(f, { required: true })} />
            </Box>
          ))}
        </Grid>
        <UserInfoFields register={register as any} />
        <Button type="submit" loading={mutation.isPending} colorScheme="teal">
          时间起卦
        </Button>
        {mutation.isError && <Text color="red.500">起卦失败，请检查输入。</Text>}
      </Stack>
    </Box>
  )
}
