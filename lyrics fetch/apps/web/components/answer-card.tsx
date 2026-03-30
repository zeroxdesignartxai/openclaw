type Props = {
  answer: string;
  meta?: Record<string, string>;
};

export default function AnswerCard({ answer, meta }: Props) {
  return (
    <div className="mt-4 rounded border border-gray-800 bg-gray-900 p-4">
      <div className="text-xl font-semibold">{answer}</div>
      {meta && (
        <dl className="mt-2 space-y-1 text-sm text-gray-300">
          {Object.entries(meta).map(([k, v]) => (
            <div key={k} className="flex gap-2">
              <dt className="uppercase text-gray-500">{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  );
}
