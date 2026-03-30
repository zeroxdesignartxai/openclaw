import { LucideIcon, Music2, Save, Sparkles, Upload, Wand2, Workflow } from "lucide-react";

const features: { title: string; description: string; icon: LucideIcon }[] = [
  {
    title: "Import anything",
    description: "MP3, WAV, or M4A plus .txt or .lrc lyrics with timestamp parsing.",
    icon: Upload
  },
  {
    title: "Manual sync",
    description: "Tap to set starts, drag on the timeline, tweak per-word fills without friction.",
    icon: Workflow
  },
  {
    title: "5 polished looks",
    description: "Minimal, Neon, Cinematic, Karaoke, and Trap presets ready for socials.",
    icon: Sparkles
  },
  {
    title: "Live preview",
    description: "Remotion-powered preview with karaoke fill, waveform, and album cover mode.",
    icon: Music2
  },
  {
    title: "Local projects",
    description: "Save and load projects in your browser storage—no account required.",
    icon: Save
  },
  {
    title: "Export ready",
    description: "One-click 1080p landscape, square, or 9:16 masters with progress UI.",
    icon: Wand2
  }
];

export function FeatureGrid() {
  return (
    <section className="grid md:grid-cols-3 gap-4">
      {features.map((feature) => (
        <div key={feature.title} className="glass-panel p-5 space-y-3 border border-white/10">
          <feature.icon className="h-6 w-6 text-primary" />
          <h3 className="font-semibold text-lg">{feature.title}</h3>
          <p className="text-sm text-white/70 leading-relaxed">{feature.description}</p>
        </div>
      ))}
    </section>
  );
}
