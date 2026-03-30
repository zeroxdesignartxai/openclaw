"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { parseLrc } from "@/lib/parse-lrc";
import { useProjectStore } from "@/hooks/use-project-store";
import { nanoid } from "nanoid";
import { Upload } from "lucide-react";

export function AudioLyricsPanel() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInput = useRef<HTMLInputElement | null>(null);
  const { project, setAudio, setLyrics } = useProjectStore();
  const [status, setStatus] = useState<string>("");

  const handleAudioUpload = async (file?: File) => {
    if (!file) return;
    const url = URL.createObjectURL(file);
    const audio = new Audio();
    audio.src = url;
    await audio.load();
    audio.onloadedmetadata = () => {
      setAudio({ url, fileName: file.name, duration: audio.duration });
      setStatus(`Loaded ${file.name}`);
    };
  };

  const handleLyricsImport = async (file?: File) => {
    if (!file) return;
    const text = await file.text();
    if (file.name.endsWith(".lrc")) {
      const lines = parseLrc(text);
      setLyrics(lines);
      setStatus(`Imported ${file.name}`);
    } else {
      const lines = text
        .split(/\n+/)
        .filter(Boolean)
        .map((line) => ({ id: nanoid(), text: line.trim(), start: 0 }));
      setLyrics(lines);
      setStatus(`Imported ${file.name}`);
    }
  };

  const handlePaste = async () => {
    const text = await navigator.clipboard.readText();
    if (!text) return;
    const lines = text
      .split(/\n+/)
      .filter(Boolean)
      .map((line) => ({ id: nanoid(), text: line.trim(), start: 0 }));
    setLyrics(lines);
    setStatus("Pasted lyrics");
  };

  return (
    <div className="glass-panel p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white/70">Audio</p>
          <p className="text-white font-medium">{project.audio?.fileName ?? "No audio yet"}</p>
        </div>
        <div className="flex gap-2">
          <Input
            ref={fileInput}
            type="file"
            accept="audio/*"
            onChange={(e) => handleAudioUpload(e.target.files?.[0])}
          />
          <Button onClick={() => fileInput.current?.click()} className="flex items-center gap-2">
            <Upload className="h-4 w-4" /> Upload
          </Button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white/70">Lyrics</p>
          <p className="text-white font-medium">{project.lyrics.length} lines</p>
        </div>
        <div className="flex gap-2">
          <Input type="file" accept=".txt,.lrc" onChange={(e) => handleLyricsImport(e.target.files?.[0])} />
          <Button variant="ghost" onClick={handlePaste}>Paste</Button>
        </div>
      </div>

      <audio ref={audioRef} src={project.audio?.url} controls className="w-full rounded-lg bg-black/30" />
      {status && <p className="text-xs text-white/60">{status}</p>}
    </div>
  );
}
