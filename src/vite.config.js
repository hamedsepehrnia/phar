import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import fs from "fs";
import handlebars from "vite-plugin-handlebars";

// مسیر فایل‌ها
const rootDir = __dirname;
const htmlFiles = fs
  .readdirSync(rootDir)
  .filter((file) => file.endsWith(".html"))
  .map((file) => path.resolve(rootDir, file));

export default defineConfig({
  base: "./",
  plugins: [
    tailwindcss(),
    handlebars({
      partialDirectory: path.resolve(__dirname, "partials"),
    }),
  ],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: htmlFiles,
      output: {
        entryFileNames: `js/bundle.js`,
        chunkFileNames: `js/bundle.js`,
        assetFileNames: ({ name }) => {
          if (/\.(gif|jpe?g|png|svg|webp)$/.test(name ?? "")) {
            return "images/[name][extname]";
          }
          if (/\.(woff2?|ttf|otf|eot)$/.test(name ?? "")) {
            return "fonts/[name][extname]";
          }
          if (/\.css$/.test(name ?? "")) {
            return "css/main.css";
          }
          return "assets/[name][extname]";
        },
      },
    },
  },
});
