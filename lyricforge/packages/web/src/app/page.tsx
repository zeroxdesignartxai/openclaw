import Link from "next/link";
import { ArrowRight, Sparkles, Wand2 } from "lucide-react";
import { PresetCarousel } from "@/components/layout/preset-carousel";
import { FeatureGrid } from "@/components/layout/feature-grid";

export default function Page() {
  return (
    <div className="space-y-10">
      <section className="glass-panel px-8 py-10 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(124,58,237,0.16),transparent_45%)]" />
        <div className="relative grid lg:grid-cols-2 gap-10 items-center">
          <div className="space-y-5">
            <p className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-primary bg-primary/10 px-3 py-1 rounded-full">
              <Sparkles className="h-4 w-4" /> Creator grade
            </p>
            <h1 className="text-4xl lg:text-5xl font-semibold leading-tight">Lyric videos built for YouTube, Reels, and TikTok in minutes.</h1>
            <p className="text-white/70 text-lg">Upload a track, paste lyrics, and sync lines with a tactile timeline. Pick a preset or craft your own look. Export crisp 1080p or vertical masters with Remotion rendering.</p>
            <div className="flex items-center gap-3">
              <Link href="/studio" className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-5 py-3 rounded-xl shadow-lg shadow-primary/30 transition">
                Open Studio <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/projects" className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-white/15 hover:border-white/30 text-white/80">
                Load Demo <Wand2 className="h-4 w-4" />
              </Link>
            </div>
          </div>
          <PresetCarousel />
        </div>
      </section>
      <FeatureGrid />
    </div>
  );
}
