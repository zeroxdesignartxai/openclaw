import { nanoid } from "nanoid";
import { type LineTiming } from "@/types/project";

const timestampRegex = /\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]/;

export function parseLrc(text: string): LineTiming[] {
  return text
    .split(/\n+/)
    .map((line) => {
      const match = line.match(timestampRegex);
      if (!match) return null;
      const [, m, s, ms] = match;
      const start = parseInt(m, 10) * 60 + parseInt(s, 10) + (ms ? parseInt(ms, 10) / 1000 : 0);
      const lyricText = line.replace(timestampRegex, "").trim();
      return { id: nanoid(), text: lyricText, start } satisfies LineTiming;
    })
    .filter(Boolean) as LineTiming[];
}
