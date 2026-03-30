import { z } from "zod";

export const wordTimingSchema = z.object({
  word: z.string(),
  start: z.number().nonnegative(),
  end: z.number().nonnegative().optional()
});

export const lineTimingSchema = z.object({
  id: z.string(),
  text: z.string(),
  start: z.number().nonnegative(),
  end: z.number().nonnegative().optional(),
  words: z.array(wordTimingSchema).optional()
});

export const backgroundOptionSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("color"), value: z.string() }),
  z.object({ kind: z.literal("gradient"), from: z.string(), to: z.string() }),
  z.object({ kind: z.literal("image"), url: z.string().url() }),
  z.object({ kind: z.literal("video"), url: z.string().url() })
]);

export const themePresetIdSchema = z.enum(["minimal", "neon", "cinematic", "karaoke", "trap"]);

export const themePresetSchema = z.object({
  id: themePresetIdSchema,
  name: z.string(),
  description: z.string(),
  typography: z.object({
    fontFamily: z.string(),
    size: z.number(),
    lineHeight: z.number(),
    weight: z.number().optional(),
    stroke: z.string().optional(),
    shadow: z.string().optional()
  }),
  colors: z.object({
    primary: z.string(),
    secondary: z.string(),
    text: z.string(),
    accent: z.string()
  }),
  layout: z.enum(["center", "bottom", "stacked"]),
  transition: z.enum(["fade", "pop", "slide", "typewriter"]),
  background: backgroundOptionSchema
});

export const exportPresetSchema = z.enum(["1080p", "vertical", "square"]);

export const projectSchema = z.object({
  id: z.string(),
  name: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
  audio: z
    .object({ url: z.string(), fileName: z.string(), duration: z.number().optional() })
    .nullable(),
  lyrics: z.array(lineTimingSchema),
  theme: themePresetIdSchema,
  options: z.object({
    captionLayout: z.enum(["center", "bottom", "stacked"]),
    karaokeFill: z.boolean(),
    showWaveform: z.boolean(),
    albumCoverUrl: z.string().optional(),
    safeMargin: z.number()
  }),
  export: z.object({
    preset: exportPresetSchema,
    quality: z.enum(["high", "medium", "draft"])
  })
});

export type WordTiming = z.infer<typeof wordTimingSchema>;
export type LineTiming = z.infer<typeof lineTimingSchema>;
export type BackgroundOption = z.infer<typeof backgroundOptionSchema>;
export type ThemePresetId = z.infer<typeof themePresetIdSchema>;
export type ThemePreset = z.infer<typeof themePresetSchema>;
export type ExportPreset = z.infer<typeof exportPresetSchema>;
export type Project = z.infer<typeof projectSchema>;

export const validateProject = (data: unknown) => projectSchema.parse(data);
