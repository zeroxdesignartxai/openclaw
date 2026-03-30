import { themePresets } from "@/components/layout/theme-presets";
import { cn } from "@/lib/utils";

const rows = [themePresets.slice(0, 3), themePresets.slice(3)];

export function PresetCarousel() {
  return (
    <div className="relative">
      <div className="absolute inset-0 blur-3xl opacity-30 bg-gradient-to-br from-primary via-secondary to-accent" />
      <div className="relative grid gap-4">
        {rows.map((row, i) => (
          <div key={i} className="grid grid-cols-3 gap-4">
            {row.map((preset) => (
              <div key={preset.id} className="glass-panel p-4 h-40 flex flex-col justify-between border-white/10">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-semibold">{preset.name}</span>
                  <span className={cn("h-2 w-2 rounded-full", preset.badge)} />
                </div>
                <div
                  className="h-20 rounded-xl border border-white/5"
                  style={{
                    background:
                      preset.background.kind === "gradient"
                        ? `linear-gradient(135deg, ${preset.background.from}, ${preset.background.to})`
                        : preset.background.kind === "color"
                          ? preset.background.value
                          : "radial-gradient(circle at 20% 20%, rgba(255,255,255,0.08), transparent 50%)"
                  }}
                />
                <p className="text-xs text-white/70 line-clamp-1">{preset.description}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
