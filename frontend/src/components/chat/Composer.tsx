import { useState, type FormEvent } from "react";

import type { UIStrings } from "../../lib/i18n";
import { MicIcon, SendIcon } from "../icons";

interface Props {
  ui: UIStrings;
  disabled: boolean;
  onSend: (text: string) => void;
  onVoice: () => void;
}

export default function Composer({ ui, disabled, onSend, onVoice }: Props) {
  const [text, setText] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <form onSubmit={submit} className="flex items-center gap-2 border-t border-line bg-surface p-3">
      <button
        type="button"
        onClick={onVoice}
        disabled={disabled}
        title={ui.voiceTitle}
        aria-label={ui.voiceTitle}
        className="grid h-10 w-10 shrink-0 place-items-center rounded-full text-ink-2 transition-colors hover:bg-canvas hover:text-brand-700 disabled:opacity-50"
      >
        <MicIcon />
      </button>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={ui.placeholder}
        maxLength={1000}
        aria-label={ui.placeholder}
        dir="auto"
        className="h-10 min-w-0 flex-1 rounded-full border border-line bg-canvas px-4 text-[15px] outline-none transition-colors placeholder:text-ink-3 focus:border-brand-300 focus:bg-surface"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        aria-label="Send"
        className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-brand-600 text-white transition-colors hover:bg-brand-700 disabled:bg-brand-200"
      >
        {/* The send arrow points along the reading direction. */}
        <SendIcon width={18} height={18} className="rtl:-scale-x-100" />
      </button>
    </form>
  );
}
