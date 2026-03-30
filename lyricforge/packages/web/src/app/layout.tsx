import type { Metadata } from "next";
import "@/styles/globals.css";
import { cn } from "@/lib/utils";
import { Outfit } from "next/font/google";
import Link from "next/link";

const outfit = Outfit({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LyricForge",
  description: "Creator-grade lyric video generator"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={cn("min-h-screen text-foreground", outfit.className)}>
        <header className="border-b border-white/10 bg-black/30 sticky top-0 backdrop-blur-md z-50">
          <div className="container flex items-center justify-between py-4">
            <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
              <span className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary to-secondary inline-flex items-center justify-center text-white font-bold">LF</span>
              <span>LyricForge</span>
            </Link>
            <nav className="flex items-center gap-4 text-sm text-white/80">
              <Link href="/studio">Studio</Link>
              <Link href="/export">Export</Link>
              <Link href="/projects">Projects</Link>
            </nav>
          </div>
        </header>
        <main className="container py-8 space-y-8">{children}</main>
      </body>
    </html>
  );
}
