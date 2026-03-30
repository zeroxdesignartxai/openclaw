import { type Project } from "@/types/project";

export const seedProject: Project = {
  id: "demo-lyricforge",
  name: "Starlight City (Demo)",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  audio: {
    url: "/demo/starlight-city.wav",
    fileName: "starlight-city.wav",
    duration: 92
  },
  lyrics: [
    { id: "l1", text: "Midnight trains cut through the haze", start: 0 },
    { id: "l2", text: "Neon signs spell out our names", start: 4 },
    { id: "l3", text: "Heartbeats keep a steady pace", start: 8 },
    { id: "l4", text: "We light the dark with razor blades", start: 12 },
    { id: "l5", text: "Ooh, we ride the skyline", start: 16 },
    { id: "l6", text: "Ooh, in ultraviolet time", start: 20 }
  ],
  theme: "neon",
  options: {
    captionLayout: "center",
    karaokeFill: true,
    showWaveform: true,
    albumCoverUrl: "/demo/starlight-cover.png",
    safeMargin: 48
  },
  export: {
    preset: "vertical",
    quality: "medium"
  }
};
