"use client";

import { themePresets } from "@/components/layout/theme-presets";
import { Button } from "@/components/ui/button";
import { useProjectStore } from "@/hooks/use-project-store";

export function ThemePicker() {
  const { project, setTheme } = useProjectStore();

  return (
    <div className="glass-panel p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white/70">Theme presets</p>
          <p className="text-white font-medium">{project.theme}</p>
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-3">
        {themePresets.map((preset) => (
          <button
            key={preset.id}
            onClick={() => setTheme(preset.id)}
            className={`rounded-xl border border-white/10 p-3 text-left transition hover:border-white/40 ${project.theme === preset.id ? "ring-2 ring-primary" : ""}`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">{preset.name}</span>
              <span className="text-xs uppercase text-white/60">{preset.layout}</span>
            </div>
            <div
              className="h-16 rounded-lg border border-white/5"
              style={{
                background:
                  preset.background.kind === "gradient"
                    ? `linear-gradient(135deg, ${preset.background.from}, ${preset.background.to})`
                    : preset.background.kind === "color"
                      ? preset.background.value
                      : "#0b1021"
              }}
            />
            <p className="text-xs text-white/70 mt-2">{preset.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
