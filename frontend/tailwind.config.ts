import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        /* Override Tailwind's amber with Claude amber palette */
        amber: {
          50: "#FBF6ED",
          100: "#F4E6CC",
          200: "#EAD0A0",
          300: "#E0BA74",
          400: "#D6A448",
          500: "#D4A853",
          600: "#C09840",
          700: "#9B7833",
          800: "#765C26",
          900: "#524019",
          950: "#2E2410",
        },
        warm: {
          base: "#FAF8F5",
          surface: "#F6F2EB",
          raised: "#FFFDF9",
          inset: "#F1ECE2",
          text: "#3D3428",
          secondary: "#6B5F50",
          muted: "#9B8E7E",
          accent: "#D4A853",
          "accent-hover": "#C09840",
          border: "#E8E0D3",
          "border-light": "#F0EBE2",
          success: "#6B9A4A",
          danger: "#C0564A",
          warning: "#D4A853",
        },
      },
      fontFamily: {
        heading: [
          '"Noto Serif SC"',
          "STSong",
          "SimSun",
          '"PingFang SC"',
          '"Microsoft YaHei"',
          "serif",
        ],
        body: [
          '"PingFang SC"',
          '"Microsoft YaHei"',
          '"Hiragino Sans GB"',
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
        mono: [
          '"JetBrains Mono"',
          '"Fira Code"',
          '"Cascadia Code"',
          "monospace",
        ],
      },
      boxShadow: {
        card: "0 1px 2px rgba(61, 52, 40, 0.04), 0 4px 16px rgba(61, 52, 40, 0.05)",
        "card-hover":
          "0 1px 2px rgba(61, 52, 40, 0.05), 0 8px 32px rgba(61, 52, 40, 0.08)",
        button: "0 2px 8px rgba(212, 168, 83, 0.22)",
      },
    },
  },
  plugins: [],
};

export default config;
