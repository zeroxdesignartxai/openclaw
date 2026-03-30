"use client";

import { AbsoluteFill, Audio, Sequence, interpolate, useCurrentFrame } from "remotion";
import { type Project, type ThemePreset } from "@/types/project";
import { themePresets } from "@/components/layout/theme-presets";
import { cn } from "@/lib/utils";

export type CompositionProps = {
  project: Project;
  durationInSeconds: number;
};

const lineHeightMap: Record<Project["options"]["captionLayout"], string> = {
  center: "items-center",
  bottom: "items-end",
  stacked: "items-center"
};

export function LyricComposition({ project, durationInSeconds }: CompositionProps) {
  const frame = useCurrentFrame();
  const fps = 30;
  const currentTime = frame / fps;
  const theme = themePresets.find((t) => t.id === project.theme) as ThemePreset;
  const { background } = theme;

  const currentLine = project.lyrics
    .slice()
    .sort((a, b) => a.start - b.start)
    .find((line, idx, arr) => {
      const next = arr[idx + 1];
      const end = next ? next.start : durationInSeconds;
      return currentTime >= line.start && currentTime < end;
    });

  return (
    <AbsoluteFill
      className="flex"
      style={{
        background:
          background.kind === "gradient"
            ? `linear-gradient(135deg, ${background.from}, ${background.to})`
            : background.kind === "color"
              ? background.value
              : "#0b1021"
      }}
    >
      {project.audio?.url && <Audio src={project.audio.url} />}
      <AbsoluteFill className={cn("px-10 flex", lineHeightMap[project.options.captionLayout])}>
        <div className="max-w-4xl mx-auto w-full" style={{ marginBottom: project.options.captionLayout === "bottom" ? 120 : 0 }}>
          <div
            className="text-center drop-shadow-xl"
            style={{
              fontFamily: theme.typography.fontFamily,
              fontSize: theme.typography.size,
              lineHeight: theme.typography.lineHeight,
              color: theme.colors.text,
              textShadow: theme.typography.shadow,
              WebkitTextStroke: theme.typography.stroke
            }}
          >
            {project.options.captionLayout === "stacked" ? (
              <div className="space-y-2">
                {project.lyrics.slice(0, 3).map((line) => (
                  <AnimatedLine key={line.id} line={line.text} active={line.id === currentLine?.id} transition={theme.transition} />
                ))}
              </div>
            ) : (
              <AnimatedLine line={currentLine?.text ?? ""} active transition={theme.transition} />
            )}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}

type AnimatedLineProps = { line: string; active: boolean; transition: ThemePreset["transition"] };

function AnimatedLine({ line, active, transition }: AnimatedLineProps) {
  const frame = useCurrentFrame();
  const fps = 30;
  const progress = interpolate(frame, [0, fps * 0.5], [0, 1], { extrapolateRight: "clamp" });

  const common = {
    opacity: active ? progress : 0.4,
    transform:
      transition === "slide"
        ? `translateY(${(1 - progress) * 20}px)`
        : transition === "pop"
          ? `scale(${0.96 + progress * 0.08})`
          : "none"
  } as const;

  return (
    <div style={common} className="font-semibold">
      {transition === "typewriter" ? <Typewriter text={line} progress={progress} /> : line}
    </div>
  );
}

function Typewriter({ text, progress }: { text: string; progress: number }) {
  const visibleCount = Math.max(1, Math.floor(text.length * progress));
  return <span>{text.slice(0, visibleCount)}</span>;
}
