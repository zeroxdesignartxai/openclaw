import "../styles/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Generate Lyrics AI",
  description: "Upload audio and generate lyric videos with AI."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
