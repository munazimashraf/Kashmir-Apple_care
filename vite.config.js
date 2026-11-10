import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: Number(process.env.VITE_PORT || 5173),
    host: true,
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
