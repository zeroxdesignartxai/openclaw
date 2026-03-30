"use client";

import { useState } from "react";
import { submitQuery } from "../lib/api";

type Props = {
  onAnswer: (answer: { text: string; meta?: Record<string, string> }) => void;
};

export default function QueryInput({ onAnswer }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await submitQuery(text);
      onAnswer({ text: res.answer, meta: res.meta });
    } catch (err: any) {
      setError(err?.message || "Failed to get answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <textarea
        className="w-full rounded border border-gray-700 bg-gray-900 p-3 text-sm"
        placeholder="Ask for a direct answer..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
      />
      <button
        type="submit"
        disabled={loading || !text.trim()}
        className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
      >
        {loading ? "Thinking…" : "Get answer"}
      </button>
      {error && <p className="text-red-400 text-sm">{error}</p>}
    </form>
  );
}
