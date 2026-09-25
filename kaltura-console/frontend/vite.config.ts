import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwind from "@tailwindcss/vite";
export default defineConfig({
  plugins: [vue(), tailwind()],
  build: { outDir: "../web/dist", emptyOutDir: true },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8080",
      "/media/": "http://127.0.0.1:8080",
    },
  },
});
