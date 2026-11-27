import { useEffect, useRef } from "react";

import type { ChatItem, Outgoing } from "../../hooks/useChat";
import { languageInfo, uiStrings, type Language, type UIStrings } from "../../lib/i18n";
import type { BotMessage } from "../../types/api";
import { AlertIcon, HomeIcon, LeafIcon } from "../icons";
import Composer from "./Composer";
import LanguageSwitcher from "./LanguageSwitcher";
import MessageBubble from "./MessageBubble";
import QuickReplies from "./QuickReplies";

interface Props {
  items: ChatItem[];
  language: Language;
  loading: boolean;
  error: string | null;
  onSend: (msg: Outgoing) => void;
  onChangeLanguage: (code: Language) => void;
  onRetry: () => void;
  onFeedback: (message: BotMessage, helpful: boolean) => void;
}

export default function ChatWindow({
  items,
  language,
  loading,
  error,
  onSend,
  onChangeLanguage,
  onRetry,
  onFeedback,
}: Props) {
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [items.length, loading, error]);

  const ui = uiStrings(language);
  const { dir } = languageInfo(language);

  // Only the latest assistant message's options are active, like a live WhatsApp thread.
  const last = items[items.length - 1];
  const activeOptions = last && last.kind === "bot" ? last.options : [];

  return (
    <section
      lang={language}
      dir={dir}
      className="flex h-[calc(100dvh-8.5rem)] min-h-[520px] flex-col overflow-hidden rounded-2xl border border-line bg-surface shadow-sm"
    >
      <header className="flex flex-wrap items-center gap-x-3 gap-y-2 border-b border-line px-4 py-3">
        <span className="grid h-10 w-10 place-items-center rounded-full bg-brand-600 text-white">
          <LeafIcon />
        </span>
        <div className="min-w-0 flex-1">
          <h2 lang="en" className="text-[15px] font-semibold leading-tight">
            Farmer Assistant
          </h2>
          <p className="text-xs text-ink-3">{loading ? ui.typing : ui.online}</p>
        </div>
        <LanguageSwitcher value={language} label={ui.language} disabled={loading} onChange={onChangeLanguage} />
        <button
          type="button"
          disabled={loading}
          onClick={() => onSend({ text: ui.home, optionId: "nav:home", label: ui.home })}
          className="inline-flex items-center gap-1.5 rounded-full border border-line px-3 py-1.5 text-sm font-medium text-ink-2 transition-colors hover:bg-canvas disabled:opacity-50"
        >
          <HomeIcon width={16} height={16} /> {ui.home}
        </button>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto bg-chat px-3 py-4 sm:px-5" aria-live="polite">
        {items.length === 0 && !loading && !error && (
          <EmptyState ui={ui} onStart={() => onSend({ text: ui.greeting })} />
        )}

        {items.map((item) => (
          <MessageBubble key={item.id} item={item} ui={ui} onFeedback={onFeedback} />
        ))}

        {!loading && !error && (
          <QuickReplies
            options={activeOptions}
            disabled={loading}
            onSelect={(o) => onSend({ text: o.label, optionId: o.id, label: o.label })}
          />
        )}

        {loading && <TypingIndicator />}

        {error && (
          <div className="mx-auto flex max-w-md items-start gap-3 rounded-xl border border-negative/30 bg-surface px-4 py-3 text-sm">
            <AlertIcon className="mt-0.5 shrink-0 text-negative" width={18} height={18} />
            <div className="flex-1">
              {/* Network errors are technical and stay in English. */}
              <p lang="en" dir="ltr" className="text-ink">
                {error}
              </p>
              <button type="button" onClick={onRetry} className="mt-1 font-medium text-brand-700 hover:underline">
                {ui.retry}
              </button>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <Composer ui={ui} disabled={loading} onSend={(text) => onSend({ text })} onVoice={() => onSend({ voice: true })} />
    </section>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-label="Assistant is typing">
      <div className="flex gap-1 rounded-2xl rounded-es-md border border-line bg-surface px-4 py-3">
        {[0, 1, 2].map((i) => (
          <span key={i} className="typing-dot h-2 w-2 rounded-full bg-ink-3" />
        ))}
      </div>
    </div>
  );
}

function EmptyState({ ui, onStart }: { ui: UIStrings; onStart: () => void }) {
  return (
    <div className="mx-auto mt-10 max-w-sm rounded-2xl border border-line bg-surface p-6 text-center">
      <span className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-brand-50 text-brand-700">
        <LeafIcon width={24} height={24} />
      </span>
      <h3 className="mt-3 font-semibold">{ui.startTitle}</h3>
      <p className="mt-1 text-sm text-ink-2">{ui.startBody}</p>
      <button
        type="button"
        onClick={onStart}
        className="mt-4 rounded-full bg-brand-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700"
      >
        “{ui.greeting}”
      </button>
    </div>
  );
}
