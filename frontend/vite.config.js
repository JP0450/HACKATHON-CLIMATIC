import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// El tablero no usa backend: lee public/resultados.json, que genera 3_reportes.py
export default defineConfig({
  plugins: [vue()],
  base: "./",
});
