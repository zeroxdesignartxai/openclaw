import { type ThemePreset } from "@/types/project";

export const themePresets: (ThemePreset & { badge: string })[] = [
  {
    id: "minimal",
    name: "Minimal",
    description: "Clean white on dark with subtle fades.",
    typography: { fontFamily: "Outfit", size: 46, lineHeight: 1.18 },
    colors: { primary: "#FFFFFF", secondary: "#94A3B8", text: "#E2E8F0", accent: "#6366F1" },
    layout: "bottom",
    transition: "fade",
    background: { kind: "color", value: "#0b1021" },
    badge: "bg-white"
  },
  {
    id: "neon",
    name: "Neon",
    description: "Vibrant cyber glow for electronic tracks.",
    typography: { fontFamily: "Space Grotesk", size: 48, lineHeight: 1.16, shadow: "0 0 16px rgba(34,211,238,0.7)" },
    colors: { primary: "#22d3ee", secondary: "#a855f7", text: "#ecfeff", accent: "#fb7185" },
    layout: "center",
    transition: "pop",
    background: { kind: "gradient", from: "#0f172a", to: "#1e1b4b" },
    badge: "bg-cyan-400"
  },
  {
    id: "cinematic",
    name: "Cinematic",
    description: "Letterboxed gold tones, smooth slides.",
    typography: { fontFamily: "Playfair Display", size: 52, lineHeight: 1.1, weight: 600 },
    colors: { primary: "#fbbf24", secondary: "#eab308", text: "#fef9c3", accent: "#f97316" },
    layout: "center",
    transition: "slide",
    background: { kind: "gradient", from: "#0f0f0f", to: "#1f2937" },
    badge: "bg-amber-400"
  },
  {
    id: "karaoke",
    name: "Karaoke",
    description: "Bold strokes, bouncing typewriter fills.",
    typography: { fontFamily: "Poppins", size: 44, lineHeight: 1.2, stroke: "2px #111" },
    colors: { primary: "#f472b6", secondary: "#c026d3", text: "#fdf2f8", accent: "#22d3ee" },
    layout: "bottom",
    transition: "typewriter",
    background: { kind: "color", value: "#0f172a" },
    badge: "bg-pink-500"
  },
  {
    id: "trap",
    name: "Trap/Urban",
    description: "Hard contrast, graffiti accent strokes.",
    typography: { fontFamily: "Anton", size: 50, lineHeight: 1.08, shadow: "4px 4px 0 #000" },
    colors: { primary: "#f8fafc", secondary: "#94a3b8", text: "#e2e8f0", accent: "#22c55e" },
    layout: "stacked",
    transition: "pop",
    background: { kind: "gradient", from: "#0b0b0b", to: "#111827" },
    badge: "bg-lime-400"
  }
];
