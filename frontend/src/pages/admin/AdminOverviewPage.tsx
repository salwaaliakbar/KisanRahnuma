import { useEffect, useState, type ReactNode } from "react";

import { getMessageUsage, getSummary } from "../../api/adminClient";
import { errorMessage } from "../../api/client";
import { AlertIcon } from "../../components/icons";
import type { DashboardSummary, MessageUsage } from "../../types/admin";

const WINDOWS = [7, 14, 30, 90];

export default function AdminOverviewPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [messages, setMessages] = useState<MessageUsage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    Promise.all([getSummary(days), getMessageUsage()])
      .then(([s, m]) => {
        if (cancelled) return;
        setSummary(s);
        setMessages(m);
      })
      .catch((err) => !cancelled && setError(errorMessage(err)));
    return () => {
      cancelled = true;
    };
  }, [days]);

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-line bg-surface p-4 text-sm text-negative">
        <AlertIcon width={16} height={16} /> {error}
      </div>
    );
  }
  if (!summary || !messages) return <p className="text-sm text-ink-3">Loading…</p>;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Overview</h1>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded-lg border border-line bg-surface px-2.5 py-1.5 text-sm"
        >
          {WINDOWS.map((d) => (
            <option key={d} value={d}>
              Last {d} days
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Tile label="Total farmers" value={summary.total_farmers} />
        <Tile label={`New (${days}d)`} value={summary.new_farmers} />
        <Tile label={`Active (${days}d)`} value={summary.active_farmers} />
        <Tile label="WhatsApp this month" value={`${messages.whatsapp_sent} / ${messages.whatsapp_free_limit}`} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Service usage">
          <ul className="space-y-2 text-sm">
            {summary.service_usage.map((s) => (
              <li key={s.service} className="flex items-center justify-between">
                <span className="text-ink-2">{s.label}</span>
                <span className="font-medium">{s.count}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Feedback">
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between">
              <span className="text-ink-2">Helpful</span>
              <span className="font-medium">{summary.feedback.helpful}</span>
            </li>
            <li className="flex items-center justify-between">
              <span className="text-ink-2">Not helpful</span>
              <span className="font-medium">{summary.feedback.not_helpful}</span>
            </li>
          </ul>
          {summary.feedback.by_service.length > 0 && (
            <ul className="mt-3 space-y-2 border-t border-line pt-3 text-sm">
              {summary.feedback.by_service.map((s) => (
                <li key={s.service} className="flex items-center justify-between">
                  <span className="text-ink-2">{s.label}</span>
                  <span className="font-medium">
                    {s.helpful} helpful · {s.not_helpful} not
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Consent">
          <dl className="space-y-2 text-sm">
            <Row label="Usage recording allowed">{summary.consent.usage_allowed}</Row>
            <Row label="Usage recording declined">{summary.consent.usage_declined}</Row>
            <Row label="Usage recording pending">{summary.consent.usage_pending}</Row>
            <Row label="Weekly updates opted in">{summary.consent.weekly_opt_in}</Row>
            <Row label="Weekly updates opted out">{summary.consent.weekly_opt_out}</Row>
          </dl>
        </Card>

        <Card title="Recent interactions">
          <ul className="space-y-2 text-sm">
            {summary.recent_interactions.map((r) => (
              <li key={r.id} className="flex items-center justify-between gap-3">
                <span className="text-ink-2">
                  <code className="text-xs text-ink-3">{r.farmer_ref}</code> · {r.service_label}: {r.description}
                </span>
                <span className="shrink-0 text-xs text-ink-3">{new Date(r.created_at).toLocaleString()}</span>
              </li>
            ))}
            {summary.recent_interactions.length === 0 && <li className="text-ink-3">No activity yet.</li>}
          </ul>
        </Card>
      </div>
    </div>
  );
}

function Tile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-line bg-surface p-4">
      <p className="text-xs text-ink-3">{label}</p>
      <p className="mt-1 text-xl font-semibold">{value}</p>
    </div>
  );
}

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-2xl border border-line bg-surface p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-ink-3">{label}</dt>
      <dd className="font-medium">{children}</dd>
    </div>
  );
}
