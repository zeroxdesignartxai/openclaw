import { NextResponse } from "next/server";

// Placeholder API; replace with Supabase + Redis wiring.
export async function POST() {
  return NextResponse.json(
    { jobId: "stub-job-id", status: "queued", note: "Wire up Supabase/Redis before use." },
    { status: 202 }
  );
}

export async function GET() {
  return NextResponse.json({ status: "stub" });
}
