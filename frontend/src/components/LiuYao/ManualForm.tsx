import { Box, Grid, NativeSelect, Stack, Text } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import axios from "axios"
import { useForm } from "react-hook-form"

import { Button } from "@/components/ui/button"
import { API_BASE, authHeaders, LINE_OPTIONS } from "./constants"
import type { HexagramReading, ManualFormValues } from "./types"
import { UserInfoFields } from "./UserInfoFields"

interface ManualFormProps {
  onResult: (r: HexagramReading) => void
}

export function ManualForm({ onResult }: ManualFormProps) {
  const { register, handleSubmit } = useForm<ManualFormValues>({
    defaultValues: { line1: 7, line2: 7, line3: 7, line4: 7, line5: 7, line6: 7 },
  })

  const mutation = useMutation({
    mutationFn: (v: ManualFormValues) =>
      axios
        .post(
          `${API_BASE}/api/v1/liuyao/cast/manual`,
          {
            lines: [v.line1, v.line2, v.line3, v.line4, v.line5, v.line6].map(Number),
            question: v.question,
            caster_name: v.caster_name,
            caster_gender: v.caster_gender,
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
          手动填写六爻（从第一爻到第六爻，由下至上）：6=老阴·变，7=少阳，8=少阴，9=老阳·变。
        </Text>
        <Grid templateColumns="repeat(6,1fr)" gap={2}>
          {([1, 2, 3, 4, 5, 6] as const).map((n) => (
            <Box key={n}>
              <Text fontSize="xs" textAlign="center" mb={1} color="gray.600">
                第{n}爻
              </Text>
              <NativeSelect.Root size="sm">
                <NativeSelect.Field {...register(`line${n}` as keyof ManualFormValues)}>
                  {LINE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.value}
                    </option>
                  ))}
                </NativeSelect.Field>
              </NativeSelect.Root>
            </Box>
          ))}
        </Grid>
        <UserInfoFields register={register as any} />
        <Button type="submit" loading={mutation.isPending} colorScheme="teal">
          提交起卦
        </Button>
        {mutation.isError && <Text color="red.500">起卦失败，请检查输入。</Text>}
      </Stack>
    </Box>
  )
}
