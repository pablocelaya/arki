import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
  },
  // Cambia la URL del backend para producción
  server: {
    proxy: {
      "/api": {
        target: "https://tu-backend-en-render.com", // Cambiar por tu URL de Render
        changeOrigin: true,
      },
    },
  },
});
