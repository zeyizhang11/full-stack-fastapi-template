import { Box, Flex, Text } from "@chakra-ui/react"

interface YaoLineShapeProps {
  value: number
  xunkong: boolean
}

/**
 * 渲染单根爻画线：
 *   7/9 → 实线（阳爻），9=老阳则橙色+○
 *   6/8 → 虚线（阴爻），6=老阴则橙色+○
 *   旬空爻用灰色表示
 */
export function YaoLineShape({ value, xunkong }: YaoLineShapeProps) {
  const isYang = value === 7 || value === 9
  const isChanging = value === 6 || value === 9
  const lineColor = isChanging ? "orange.500" : xunkong ? "gray.400" : "gray.800"

  return (
    <Flex align="center" gap={1} minW="80px">
      {isYang ? (
        <Box h="4px" w="80px" bg={lineColor} borderRadius="sm" flexShrink={0} />
      ) : (
        <Flex gap={1} flexShrink={0}>
          <Box h="4px" w="36px" bg={lineColor} borderRadius="sm" />
          <Box h="4px" w="36px" bg={lineColor} borderRadius="sm" />
        </Flex>
      )}
      {isChanging && (
        <Text fontSize="xs" color="orange.500" ml={1}>○</Text>
      )}
    </Flex>
  )
}
