import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      colors: {
        brand: { DEFAULT: "#5E6AD2", light: "#EEF0FF", dark: "#4B55C4" },
        neutral: {
          0: "#FFFFFF",
          50: "#F8F9FA",
          100: "#F1F3F5",
          200: "#E9ECEF",
          300: "#DEE2E6",
          400: "#CED4DA",
          500: "#ADB5BD",
          600: "#6C757D",
          700: "#495057",
          800: "#343A40",
          900: "#212529",
        },
        success: { DEFAULT: "#12B76A", light: "#ECFDF5" },
        warning: { DEFAULT: "#F79009", light: "#FFFAEB" },
        danger: { DEFAULT: "#F04438", light: "#FEF3F2" },
        info: { DEFAULT: "#0EA5E9", light: "#F0F9FF" },
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        "card-hover": "0 4px 12px rgba(0,0,0,0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
