/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/app/**/*.{ts,tsx}"
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem"
    },
    extend: {
      fontFamily: {
        display: ["'Poppins'", "'Inter'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        accent: ["'Space Grotesk'", "'Inter'", "sans-serif"]
      },
      colors: {
        background: "hsl(222.2 84% 4.9%)",
        foreground: "hsl(210 40% 98%)",
        muted: {
          DEFAULT: "hsl(217.2 32.6% 17.5%)",
          foreground: "hsl(215 20.2% 65.1%)"
        },
        primary: {
          DEFAULT: "#7C3AED",
          foreground: "#F8FAFC"
        },
        secondary: {
          DEFAULT: "#0EA5E9",
          foreground: "#E0F2FE"
        },
        accent: {
          DEFAULT: "#F97316",
          foreground: "#FFF7ED"
        }
      },
      boxShadow: {
        glass: "0 10px 40px rgba(0,0,0,0.35)"
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-700px 0" },
          "100%": { backgroundPosition: "700px 0" }
        }
      },
      animation: {
        shimmer: "shimmer 2s linear infinite"
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};
