import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "node:fs";
import { parse as parseEnv } from "dotenv";

function loadSecretEnv(): Record<string, string> {
  try {
    return parseEnv(readFileSync(".env.secret"));
  } catch {
    return {};
  }
}

export default defineConfig(({ mode }) => {
  const env = { ...loadEnv(mode, process.cwd(), ""), ...loadSecretEnv() };
  const target = env.VITE_API_TARGET || "http://127.0.0.1:8000";

  return {
    plugins: [react()],
    server: {
      proxy: {
        "/auth": { target, changeOrigin: true },
        "/flashcards": { target, changeOrigin: true },
        "/items": { target, changeOrigin: true },
        "/learners": { target, changeOrigin: true },
        "/interactions": { target, changeOrigin: true },
        "/analytics": { target, changeOrigin: true },
        "/pipeline": { target, changeOrigin: true },
        "/docs": { target, changeOrigin: true },
        "/openapi.json": { target, changeOrigin: true },
      },
    },
  };
});
