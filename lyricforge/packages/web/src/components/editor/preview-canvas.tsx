"use client";

import { Player } from "@remotion/player";
import { useMemo } from "react";
import { useProjectStore } from "@/hooks/use-project-store";
import { type CompositionProps, LyricComposition } from "@/components/editor/remotion-composition";

export function PreviewCanvas() {
  const { project } = useProjectStore();

  const props = useMemo<CompositionProps>(() => ({
    project,
    durationInSeconds: project.audio?.duration ?? 60
  }), [project]);

  const presetToSize = {
    "1080p": { width: 1920, height: 1080 },
    vertical: { width: 1080, height: 1920 },
    square: { width: 1080, height: 1080 }
  } as const;

  const size = presetToSize[project.export.preset];

  return (
    <div className="glass-panel p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-white/70">Live preview</p>
        <p className="text-xs text-white/50">
          {size.width}x{size.height}
        </p>
      </div>
      <Player
        component={LyricComposition}
        inputProps={props}
        durationInFrames={Math.floor((project.audio?.duration ?? 60) * 30)}
        fps={30}
        compositionWidth={size.width}
        compositionHeight={size.height}
        style={{ borderRadius: 16, border: "1px solid rgba(255,255,255,0.08)" }}
        acknowledgeRemotionLicense
        controls
      />
    </div>
  );
}
