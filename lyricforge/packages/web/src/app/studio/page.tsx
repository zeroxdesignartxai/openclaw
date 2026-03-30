"use client";

import { AudioLyricsPanel } from "@/components/editor/audio-lyrics-panel";
import { TimelineEditor } from "@/components/editor/timeline";
import { ThemePicker } from "@/components/editor/theme-picker";
import { PreviewCanvas } from "@/components/editor/preview-canvas";
import { Button } from "@/components/ui/button";
import { useProjectStore } from "@/hooks/use-project-store";
import { Save } from "lucide-react";

export default function StudioPage() {
  const { upsertProjectToLocal } = useProjectStore();

  return (
    <div className="grid xl:grid-cols-[1.1fr,0.9fr] gap-6">
      <div className="space-y-4">
        <AudioLyricsPanel />
        <TimelineEditor />
      </div>
      <div className="space-y-4">
        <PreviewCanvas />
        <ThemePicker />
        <Button onClick={upsertProjectToLocal} className="w-full flex items-center gap-2 justify-center">
          <Save className="h-4 w-4" /> Save project locally
        </Button>
      </div>
    </div>
  );
}
