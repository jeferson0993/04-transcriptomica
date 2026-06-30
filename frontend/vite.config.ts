import { defineConfig } from "vite";

export default defineConfig({
  base: "/transcriptomics/",
  server: {
    port: 5173,
    proxy: {
      "/api/transcriptomics": {
        target: "http://localhost:8003",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
