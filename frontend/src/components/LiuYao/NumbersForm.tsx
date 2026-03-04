import { Box, Grid, Input, Stack, Text } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import axios from "axios"
import { useForm } from "react-hook-form"

import { Button } from "@/components/ui/button"
import { API_BASE, authHeaders } from "./constants"
import type { HexagramReading, NumbersFormValues } from "./types"
import { UserInfoFields } from "./UserInfoFields"

interface NumbersFormProps {
  onResult: (r: HexagramReading) => void
}

export function NumbersForm({ onResult }: NumbersFormProps) {
  const { register, handleSubmit } = useForm<NumbersFormValues>()

  const mutation = useMutation({
    mutationFn: (v: NumbersFormValues) =>
      axios
        .post(
          `${API_BASE}/api/v1/liuyao/cast/numbers`,
          {
            ...v,
            upper_num: Number(v.upper_num),
            lower_num: Number(v.lower_num),
            changing_num: Number(v.changing_num),
          },
          { headers: authHeaders() },
        )
        .then((r) => r.data),
    onSuccess: onResult,
  })

  return (
    <Box as="form" onSubmit={handleSubmit((v) => mutation.mutate(v))}>
      <Stack gap={4}>
        <Text color="gray.600" fontSize="sm">
          心中默念三个数字，依次填入。上卦数 mod 8 得上卦，下卦数 mod 8 得下卦，动爻数 mod 6 得变爻。
        </Text>
        <Grid templateColumns={{ base: "1fr", md: "1fr 1fr 1fr" }} gap={3}>
          <Box>
            <Text fontSize="sm" mb={1} color="gray.600">上卦数</Text>
            <Input
              type="number"
              placeholder="任意整数"
              {...register("upper_num", { required: true, min: 1 })}
            />
          </Box>
          <Box>
            <Text fontSize="sm" mb={1} color="gray.600">下卦数</Text>
            <Input
              type="number"
              placeholder="任意整数"
              {...register("lower_num", { required: true, min: 1 })}
            />
          </Box>
          <Box>
            <Text fontSize="sm" mb={1} color="gray.600">动爻数</Text>
            <Input
              type="number"
              placeholder="任意整数"
              {...register("changing_num", { required: true, min: 1 })}
            />
          </Box>
        </Grid>
        <UserInfoFields register={register as any} />
        <Button type="submit" loading={mutation.isPending} colorScheme="teal">
          报数起卦
        </Button>
        {mutation.isError && <Text color="red.500">起卦失败，请检查输入。</Text>}
      </Stack>
    </Box>
  )
}
