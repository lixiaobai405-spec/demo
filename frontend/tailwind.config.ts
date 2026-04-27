import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          ink: "#0f172a",
          mist: "#dbeafe",
          gold: "#f59e0b",
          cyan: "#38bdf8",
        },
      },
    },
  },
  plugins: [],
};

export default config;

