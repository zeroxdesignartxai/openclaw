import AnswerCard from "../../../components/answer-card";
import { fetchResult } from "../../../lib/api";

export default async function ResultPage({ params }: { params: { id: string } }) {
  const data = await fetchResult(params.id);
  return (
    <main className="min-h-screen max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-semibold mb-4">Result</h1>
      <AnswerCard answer={data.answer} meta={data.meta} />
    </main>
  );
}
