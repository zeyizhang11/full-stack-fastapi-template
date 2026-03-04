import path from "node:path"
import { TanStackRouterVite } from "@tanstack/router-vite-plugin"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  plugins: [react(), TanStackRouterVite()],
  server: {
    // Windows + Docker 下文件系统事件无法透传，需开启轮询才能热更新
    watch: {
      usePolling: true,
      interval: 500,
    },
  },
})
