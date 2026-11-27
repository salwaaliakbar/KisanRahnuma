import { useEffect, useState } from "react";

import { getFarmers } from "../../api/adminClient";
import { errorMessage } from "../../api/client";
import { AlertIcon } from "../../components/icons";
import type { FarmerPage } from "../../types/admin";

const PAGE_SIZE = 20;

export default function AdminFarmersPage() {
  const [page, setPage] = useState<FarmerPage | null>(null);
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    getFarmers(offset, PAGE_SIZE)
      .then((p) => !cancelled && setPage(p))
      .catch((err) => !cancelled && setError(errorMessage(err)));
    return () => {
      cancelled = true;
    };
  }, [offset]);

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-line bg-surface p-4 text-sm text-negative">
        <AlertIcon width={16} height={16} /> {error}
      </div>
    );
  }
  if (!page) return <p className="text-sm text-ink-3">Loading…</p>;

  const from = page.total === 0 ? 0 : page.offset + 1;
  const to = Math.min(page.offset + page.items.length, page.total);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Farmers</h1>
        <p className="text-sm text-ink-3">
          {from}–{to} of {page.total}
        </p>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-line bg-surface">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-line text-xs uppercase tracking-wide text-ink-3">
            <tr>
              <th className="px-4 py-2.5 font-medium">Farmer ID</th>
              <th className="px-4 py-2.5 font-medium">Channel</th>
              <th className="px-4 py-2.5 font-medium">Language</th>
              <th className="px-4 py-2.5 font-medium">District</th>
              <th className="px-4 py-2.5 font-medium">Usage consent</th>
              <th className="px-4 py-2.5 font-medium">Weekly updates</th>
              <th className="px-4 py-2.5 font-medium">Joined</th>
            </tr>
          </thead>
          <tbody>
            {page.items.map((f) => (
              <tr key={f.farmer_id} className="border-b border-line last:border-0">
                <td className="px-4 py-2.5">
                  <code className="text-xs text-ink-3">{f.farmer_id.slice(0, 8)}…</code>
                </td>
                <td className="px-4 py-2.5 text-ink-2">{f.channel}</td>
                <td className="px-4 py-2.5 text-ink-2">{f.language}</td>
                <td className="px-4 py-2.5 text-ink-2">{f.district ?? "—"}</td>
                <td className="px-4 py-2.5 text-ink-2">{yesNo(f.usage_consent)}</td>
                <td className="px-4 py-2.5 text-ink-2">{yesNo(f.weekly_updates)}</td>
                <td className="px-4 py-2.5 text-ink-3">{new Date(f.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
            {page.items.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-ink-3">
                  No farmers yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-end gap-2">
        <button
          type="button"
          disabled={offset === 0}
          onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
          className="rounded-lg border border-line px-3 py-1.5 text-sm font-medium text-ink-2 transition-colors hover:bg-canvas disabled:opacity-50"
        >
          Previous
        </button>
        <button
          type="button"
          disabled={to >= page.total}
          onClick={() => setOffset(offset + PAGE_SIZE)}
          className="rounded-lg border border-line px-3 py-1.5 text-sm font-medium text-ink-2 transition-colors hover:bg-canvas disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}

function yesNo(value: boolean | null): string {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return "Not answered";
}
