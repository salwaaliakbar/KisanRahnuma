import type { ReactNode } from "react";

import type { Outgoing } from "../../hooks/useChat";
import { formatState } from "../../lib/format";
import { languageInfo, type Language } from "../../lib/i18n";
import type { ConsentStatus } from "../../types/api";
import { UserPlusIcon } from "../icons";

interface Props {
  clientId: string;
  state: string | null;
  language: Language;
  consent: ConsentStatus | null;
  loading: boolean;
  onNewFarmer: () => void;
  onSend: (msg: Outgoing) => void;
}

const SAMPLE_INPUTS = [
  "Hi",
  "Weather",
  "Crop rates",
  "When should I sow wheat?",
  "How to control pink bollworm",
  "How much urea for wheat?",
  "What is the price of gold?",
  "language",
  "اردو",
  "گندم کب کاشت کریں؟",
  "سنڌي",
  "ڪڻڪ کي ڪيترو ڀاڻ گهرجي؟",
];

/** Developer side panel: session details and sample inputs for testing. */
export default function SessionPanel({ clientId, state, language, consent, loading, onNewFarmer, onSend }: Props) {
  return (
    <aside className="space-y-4">
      <div className="rounded-2xl border border-line bg-surface p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Test session</h3>
          <span className="rounded-full bg-canvas px-2 py-0.5 text-[11px] font-medium text-ink-3">web channel</span>
        </div>
        <dl className="mt-3 space-y-2.5 text-sm">
          <Row label="Browser ID">
            <code className="text-xs text-ink-2">{clientId.slice(0, 8)}…</code>
          </Row>
          <Row label="Farmer ID">
            <code className="text-xs text-ink-2">{consent ? `${consent.farmer_id.slice(0, 8)}…` : "Not created"}</code>
          </Row>
          <Row label="Conversation step">
            <span className="text-ink-2">{state ? formatState(state) : "Not started"}</span>
          </Row>
          <Row label="Language">
            <span lang={language} className="text-ink-2">
              {languageInfo(language).name}
            </span>
          </Row>
          <Row label="Usage recording">
            <Pill value={consent?.usage_consent} />
          </Row>
          <Row label="Weekly updates">
            <Pill value={consent?.weekly_updates} />
          </Row>
        </dl>
        <button
          type="button"
          onClick={onNewFarmer}
          disabled={loading}
          className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-line px-3 py-2 text-sm font-medium text-ink-2 transition-colors hover:bg-canvas disabled:opacity-50"
        >
          <UserPlusIcon width={16} height={16} /> Start as a new farmer
        </button>
      </div>

      <div className="rounded-2xl border border-line bg-surface p-4">
        <h3 className="text-sm font-semibold">Try these messages</h3>
        <p className="mt-1 text-xs text-ink-3">Typed exactly as a farmer would. The backend decides every reply.</p>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {SAMPLE_INPUTS.map((text) => (
            <button
              key={text}
              type="button"
              disabled={loading}
              onClick={() => onSend({ text })}
              dir="auto"
              className="rounded-lg border border-line bg-canvas px-2.5 py-1 text-xs text-ink-2 transition-colors hover:border-brand-300 hover:text-brand-700 disabled:opacity-50"
            >
              {text}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-ink-3">{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}

function Pill({ value }: { value: boolean | null | undefined }) {
  if (value === true) return <span className="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">Yes</span>;
  if (value === false) return <span className="rounded-full bg-canvas px-2 py-0.5 text-xs font-medium text-ink-2">No</span>;
  return <span className="text-xs text-ink-3">Not answered</span>;
}
