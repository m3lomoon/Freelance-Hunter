import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Monochrome system — deep blacks → slate grays
        ink: {
          950: "#050506",
          900: "#0a0a0c",
          850: "#0e0e11",
          800: "#121216",
          700: "#1a1a1f",
          600: "#23232a",
          500: "#2e2e36",
        },
        slate: {
          fog: "#6b6b76",
          mist: "#9a9aa6",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        editorial: "0.28em",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,0.06), 0 0 24px -6px rgba(255,255,255,0.12)",
        "glow-strong":
          "0 0 0 1px rgba(255,255,255,0.12), 0 0 40px -8px rgba(255,255,255,0.22)",
        inset: "inset 0 1px 0 0 rgba(255,255,255,0.04)",
      },
      backgroundImage: {
        "grain":
          "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.025) 1px, transparent 0)",
      },
      keyframes: {
        pulseGlow: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        pulseGlow: "pulseGlow 2.4s ease-in-out infinite",
        shimmer: "shimmer 2s infinite",
      },
    },
  },
  plugins: [],
};

export default config;
