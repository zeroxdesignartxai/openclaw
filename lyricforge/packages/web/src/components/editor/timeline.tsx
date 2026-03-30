"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useProjectStore } from "@/hooks/use-project-store";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { type LineTiming } from "@/types/project";
import { GripVertical, Play, Pause, Clock } from "lucide-react";

const formatTime = (value: number) => {
  const m = Math.floor(value / 60)
    .toString()
    .padStart(2, "0");
  const s = Math.floor(value % 60)
    .toString()
    .padStart(2, "0");
  const ms = Math.floor((value % 1) * 1000)
    .toString()
    .padStart(3, "0");
  return `${m}:${s}.${ms}`;
};

export function TimelineEditor() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const { project, updateLine, setLyrics } = useProjectStore();
  const [playing, setPlaying] = useState(false);

  const sortedLyrics = useMemo(
    () => [...project.lyrics].sort((a, b) => a.start - b.start),
    [project.lyrics]
  );

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    playing ? audio.play() : audio.pause();
  }, [playing]);

  const setFromCurrentTime = (line: LineTiming) => {
    const audio = audioRef.current;
    if (!audio) return;
    updateLine(line.id, { start: audio.currentTime });
  };

  const reorder = (index: number, delta: number) => {
    const next = [...sortedLyrics];
    const targetIndex = index + delta;
    if (targetIndex < 0 || targetIndex >= next.length) return;
    const [item] = next.splice(index, 1);
    next.splice(targetIndex, 0, item);
    setLyrics(next.map((line, idx) => ({ ...line, start: Math.max(line.start, idx * 2) })));
  };

  return (
    <div className="glass-panel p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-white/70">
          <Clock className="h-4 w-4" /> Timeline
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => setPlaying((p) => !p)} className="flex items-center gap-2">
            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />} {playing ? "Pause" : "Play"}
          </Button>
        </div>
      </div>

      <audio ref={audioRef} src={project.audio?.url} />

      <div className="space-y-3">
        {sortedLyrics.map((line, idx) => (
          <div key={line.id} className="grid grid-cols-[auto,1fr,140px,auto] gap-3 items-center bg-white/5 rounded-xl px-3 py-2">
            <div className="flex items-center gap-2 text-xs text-white/50">
              <GripVertical className="h-4 w-4" />
              <span>{idx + 1}</span>
            </div>
            <p className="truncate">{line.text}</p>
            <div className="text-right text-sm font-mono tabular-nums">{formatTime(line.start)}</div>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => setFromCurrentTime(line)} className="text-xs">
                Set from now
              </Button>
              <Button variant="outline" onClick={() => reorder(idx, -1)} className="text-xs">↑</Button>
              <Button variant="outline" onClick={() => reorder(idx, 1)} className="text-xs">↓</Button>
            </div>
            <div className="col-span-4">
              <Slider
                min={0}
                max={project.audio?.duration ?? 180}
                step={0.05}
                value={line.start}
                onChange={(e) => updateLine(line.id, { start: Number(e.target.value) })}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
