"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useProjectStore } from "@/hooks/use-project-store";
import { Download, Loader2 } from "lucide-react";

const presetOptions = [
  { id: "1080p", label: "YouTube 1920x1080" },
  { id: "vertical", label: "TikTok / Reels 1080x1920" },
  { id: "square", label: "Square 1080x1080" }
] as const;

export function ExportPanel() {
  const { project } = useProjectStore();
  const [progress, setProgress] = useState<number>(0);
  const [status, setStatus] = useState<string>("Idle");

  const startExport = async () => {
    setStatus("Rendering with Remotion...");
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((res) => setTimeout(res, 120));
      setProgress(i);
    }
    setStatus("Export ready (mock)");
  };

  return (
    <div className="glass-panel p-4 space-y-4">
      <div>
        <p className="text-sm text-white/70">Export preset</p>
        <div className="grid gap-2 mt-2">
          {presetOptions.map((option) => (
            <label key={option.id} className="flex items-center gap-2 text-sm text-white/80">
              <input type="radio" name="preset" defaultChecked={project.export.preset === option.id} />
              {option.label}
            </label>
          ))}
        </div>
      </div>

      <div>
        <p className="text-sm text-white/70 mb-2">Quality</p>
        <div className="flex gap-2 text-sm text-white/80">
          <span className="px-3 py-1 rounded-full bg-white/10">High</span>
          <span className="px-3 py-1 rounded-full bg-white/5">Medium</span>
          <span className="px-3 py-1 rounded-full bg-white/5">Draft</span>
        </div>
      </div>

      <Slider label="Safe margin" min={0} max={120} step={4} value={project.options.safeMargin} readOnly />

      <div className="space-y-2">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary to-secondary" style={{ width: `${progress}%` }} />
        </div>
        <p className="text-xs text-white/60">{status}</p>
      </div>

      <Button onClick={startExport} className="w-full flex items-center gap-2 justify-center">
        {progress > 0 && progress < 100 ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
        Start export (mock)
      </Button>
    </div>
  );
}
