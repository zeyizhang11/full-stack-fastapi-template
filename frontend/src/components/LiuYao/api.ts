import axios from "axios"
import type { HexagramInfo, HexagramReading } from "./types"
import { API_BASE, authHeaders } from "./constants"

// ─── API 请求函数 ──────────────────────────────────────────────────────────────

export async function fetchHistory(): Promise<HexagramReading[]> {
  const { data } = await axios.get(`${API_BASE}/api/v1/liuyao/`, {
    headers: authHeaders(),
  })
  return data.data
}

export async function fetchHexagrams(): Promise<Record<string, HexagramInfo>> {
  const { data } = await axios.get(`${API_BASE}/api/v1/liuyao/hexagrams`)
  return data
}

export async function deleteReading(id: string): Promise<void> {
  await axios.delete(`${API_BASE}/api/v1/liuyao/${id}`, {
    headers: authHeaders(),
  })
}
