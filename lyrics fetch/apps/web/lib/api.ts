const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function submitQuery(input: string) {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input }),
  });
  if (!res.ok) throw new Error("API error");
  return res.json();
}

export async function fetchResult(id: string) {
  const res = await fetch(`${API_BASE}/api/result/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Result not found");
  return res.json();
}
