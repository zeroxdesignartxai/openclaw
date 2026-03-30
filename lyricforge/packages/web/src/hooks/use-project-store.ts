"use client";

import { create } from "zustand";
import { nanoid } from "nanoid";
import { type LineTiming, type Project, type ThemePresetId } from "@/types/project";
import { seedProject } from "@/data/seedProject";

export type ProjectState = {
  project: Project;
  loadProject: (project: Project) => void;
  setTheme: (id: ThemePresetId) => void;
  setLyrics: (lyrics: LineTiming[]) => void;
  updateLine: (id: string, partial: Partial<LineTiming>) => void;
  setAudio: (payload: Project["audio"]) => void;
  upsertProjectToLocal: () => void;
  loadFromLocal: (id?: string) => void;
};

const STORAGE_KEY = "lyricforge-projects";

const createEmptyProject = (): Project => ({
  id: nanoid(),
  name: "Untitled",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  audio: null,
  lyrics: [],
  theme: "minimal",
  options: {
    captionLayout: "center",
    karaokeFill: true,
    showWaveform: true,
    safeMargin: 48
  },
  export: { preset: "1080p", quality: "medium" }
});

export const useProjectStore = create<ProjectState>((set, get) => ({
  project: seedProject,
  loadProject: (project) => set({ project }),
  setTheme: (id) => set((state) => ({ project: { ...state.project, theme: id, updatedAt: new Date().toISOString() } })),
  setLyrics: (lyrics) => set((state) => ({ project: { ...state.project, lyrics, updatedAt: new Date().toISOString() } })),
  updateLine: (id, partial) =>
    set((state) => ({
      project: {
        ...state.project,
        lyrics: state.project.lyrics.map((line) => (line.id === id ? { ...line, ...partial } : line)),
        updatedAt: new Date().toISOString()
      }
    })),
  setAudio: (payload) => set((state) => ({ project: { ...state.project, audio: payload, updatedAt: new Date().toISOString() } })),
  upsertProjectToLocal: () => {
    const list = getLocal();
    const current = get().project;
    const filtered = list.filter((p) => p.id !== current.id);
    const payload = [...filtered, { ...current, updatedAt: new Date().toISOString() }];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  },
  loadFromLocal: (id) => {
    const list = getLocal();
    if (!list.length) return;
    const match = id ? list.find((p) => p.id === id) : list[list.length - 1];
    if (match) set({ project: match });
  }
}));

const getLocal = (): Project[] => {
  if (typeof window === "undefined") return [];
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw) as Project[];
  } catch (err) {
    console.error("Failed to parse local projects", err);
    return [];
  }
};

export { createEmptyProject };
