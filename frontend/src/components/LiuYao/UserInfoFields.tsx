import { Box, Grid, Input, NativeSelect, Text } from "@chakra-ui/react"
import type { UseFormRegister, FieldValues } from "react-hook-form"

interface UserInfoFieldsProps {
  register: UseFormRegister<FieldValues>
}

/**
 * 姓名 / 性别 / 占事 公共表单字段
 * 供三铜钱法、时间起卦、报数起卦、手动填爻共用
 */
export function UserInfoFields({ register }: UserInfoFieldsProps) {
  return (
    <Grid templateColumns={{ base: "1fr", md: "1fr 1fr 2fr" }} gap={3}>
      <Box>
        <Text fontSize="sm" mb={1} color="gray.600">姓名（选填）</Text>
        <Input placeholder="请输入姓名" {...register("caster_name")} />
      </Box>
      <Box>
        <Text fontSize="sm" mb={1} color="gray.600">性别（选填）</Text>
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
        <Text fontSize="sm" mb={1} color="gray.600">占事（选填）</Text>
        <Input placeholder="如：今日出行、感情运势…" {...register("question")} />
      </Box>
    </Grid>
  )
}
