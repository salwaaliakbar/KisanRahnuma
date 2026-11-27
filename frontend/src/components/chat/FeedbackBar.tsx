import type { FeedbackState } from "../../hooks/useChat";
import type { UIStrings } from "../../lib/i18n";
import { ThumbDownIcon, ThumbUpIcon } from "../icons";

interface Props {
  ui: UIStrings;
  state?: FeedbackState;
  onVote: (helpful: boolean) => void;
}

/** Helpful Yes/No buttons shown inside the answer bubble (same message, as on WhatsApp). */
export default function FeedbackBar({ ui, state, onVote }: Props) {
  if (state === "yes" || state === "no") {
    return (
      <div className="mt-2 border-t border-line pt-2 text-xs text-ink-2">
        {state === "yes" ? ui.thanksYes : ui.thanksNo}
      </div>
    );
  }

  const busy = state === "sending";
  const btn =
    "inline-flex items-center gap-1.5 rounded-full border border-line px-3 py-1 text-xs font-medium text-ink-2 transition-colors hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 disabled:opacity-50";

  return (
    <div className="mt-2 flex flex-wrap items-center gap-2 border-t border-line pt-2">
      <span className="text-xs text-ink-3">{ui.helpfulQ}</span>
      <button type="button" className={btn} disabled={busy} onClick={() => onVote(true)}>
        <ThumbUpIcon width={14} height={14} /> {ui.helpfulYes}
      </button>
      <button type="button" className={btn} disabled={busy} onClick={() => onVote(false)}>
        <ThumbDownIcon width={14} height={14} /> {ui.helpfulNo}
      </button>
      {state === "error" && <span className="text-xs text-negative">{ui.feedbackError}</span>}
    </div>
  );
}
