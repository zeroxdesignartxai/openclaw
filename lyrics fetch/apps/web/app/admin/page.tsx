import Link from "next/link";

export default function AdminPage() {
  return (
    <main className="min-h-screen max-w-3xl mx-auto px-4 py-10 space-y-4">
      <h1 className="text-3xl font-semibold">Admin</h1>
      <p className="text-sm text-gray-300">Manage categories, connectors, and rules (stub page for MVP).</p>
      <ul className="list-disc list-inside space-y-2">
        <li>Categories: API at /api/admin/categories</li>
        <li>Connectors: API at /api/admin/connectors</li>
        <li>Rules: API at /api/admin/rules</li>
      </ul>
      <Link href="/" className="text-blue-400 underline">
        ← Back to query
      </Link>
    </main>
  );
}
