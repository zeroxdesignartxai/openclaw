"use client";

import { FormEvent, useState } from "react";

type JobStatus = "idle" | "creating" | "queued" | "processing" | "done" | "failed";

export default function Home() {
  const [status, setStatus] = useState<JobStatus>("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("creating");
    setMessage("Stub: wire to /api/jobs when backend is ready.");
    // TODO: connect to server action to create job and start polling.
  };

  return (
    <main className="min-h-screen flex flex-col items-center px-6 py-10">
      <div className="max-w-3xl w-full space-y-6">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold text-white">Generate Lyrics AI</h1>
          <p className="text-slate-300">
            Upload a track or paste a YouTube link; we&apos;ll transcribe, align, and render lyric videos in 16:9 and 9:16.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-lg p-6 space-y-4 shadow-lg">
          <div className="space-y-2">
            <label className="block text-sm text-slate-300">Audio file (MP3/MP4) or YouTube URL</label>
            <input
              type="file"
              accept="audio/*,video/*"
              className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100"
            />
            <input
              type="url"
              placeholder="https://youtube.com/..."
              className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <label className="flex items-center gap-2 text-sm text-slate-200">
              <input type="radio" name="theme" value="gradient" defaultChecked className="accent-purple-500" /> Gradient
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-200">
              <input type="radio" name="theme" value="cover-blur" className="accent-purple-500" /> Cover blur
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-200">
              <input type="radio" name="theme" value="vhs" className="accent-purple-500" /> VHS
            </label>
          </div>

          <label className="inline-flex items-center gap-2 text-sm text-slate-200">
            <input type="checkbox" name="aiImages" className="accent-purple-500" /> Generate AI scene images (may use credits)
          </label>

          <button
            type="submit"
            className="rounded bg-gradient-to-r from-purple-600 to-pink-500 px-4 py-2 text-sm font-medium text-white shadow hover:brightness-110"
          >
            Create job
          </button>

          {status !== "idle" && (
            <p className="text-xs text-slate-400">
              Status: {status}. {message}
            </p>
          )}
        </form>

        <section className="bg-slate-900 border border-slate-800 rounded-lg p-4 space-y-2">
          <h2 className="text-lg font-semibold text-white">What happens next</h2>
          <ol className="text-sm text-slate-300 space-y-1 list-decimal list-inside">
            <li>We upload your audio to Supabase storage.</li>
            <li>Worker transcribes with Whisper, generates SRT/JSON, renders 16:9 and 9:16 videos.</li>
            <li>When ready, you can download MP4 and SRT.</li>
          </ol>
        </section>
      </div>
    </main>
  );
}
