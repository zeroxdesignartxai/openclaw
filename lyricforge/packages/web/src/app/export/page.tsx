"use client";

import { ExportPanel } from "@/components/export/export-panel";
import { PreviewCanvas } from "@/components/editor/preview-canvas";

export default function ExportPage() {
  return (
    <div className="grid xl:grid-cols-[1.1fr,0.9fr] gap-6">
      <PreviewCanvas />
      <ExportPanel />
    </div>
  );
}
