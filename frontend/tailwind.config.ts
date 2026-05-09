import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        /* Keep existing warm palette for backward compat */
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

        /* shadcn semantic colors — mapped to CLAUDE AMBER palette */
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        card: {
          DEFAULT: "hsl(var(--card) / <alpha-value>)",
          foreground: "hsl(var(--card-foreground) / <alpha-value>)",
        },
        popover: {
          DEFAULT: "hsl(var(--popover) / <alpha-value>)",
          foreground: "hsl(var(--popover-foreground) / <alpha-value>)",
        },
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary) / <alpha-value>)",
          foreground: "hsl(var(--secondary-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "hsl(var(--accent) / <alpha-value>)",
          foreground: "hsl(var(--accent-foreground) / <alpha-value>)",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
          foreground: "hsl(var(--destructive-foreground) / <alpha-value>)",
        },
        border: "hsl(var(--border) / <alpha-value>)",
        input: "hsl(var(--input) / <alpha-value>)",
        ring: "hsl(var(--ring) / <alpha-value>)",
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-background) / <alpha-value>)",
          foreground: "hsl(var(--sidebar-foreground) / <alpha-value>)",
          primary: "hsl(var(--sidebar-primary) / <alpha-value>)",
          "primary-foreground":
            "hsl(var(--sidebar-primary-foreground) / <alpha-value>)",
          accent: "hsl(var(--sidebar-accent) / <alpha-value>)",
          "accent-foreground":
            "hsl(var(--sidebar-accent-foreground) / <alpha-value>)",
          border: "hsl(var(--sidebar-border) / <alpha-value>)",
          ring: "hsl(var(--sidebar-ring) / <alpha-value>)",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
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
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        fadeIn: {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "in": "fadeIn 0.4s ease both",
      },
    },
  },
  plugins: [],
};

export default config;
