"use client";
import QueryInput from "../components/query-input";
import AnswerCard from "../components/answer-card";
import { useState } from "react";

export default function HomePage() {
  const [answer, setAnswer] = useState<{ text: string; meta?: Record<string, string> } | null>(null);

  return (
    <main className="min-h-screen max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-semibold mb-6">Direct Answer Engine</h1>
      <QueryInput onAnswer={setAnswer} />
      {answer && <AnswerCard answer={answer.text} meta={answer.meta} />}
    </main>
  );
}
