import type { ChatOption } from "../../types/api";
import { HomeIcon } from "../icons";

interface Props {
  options: ChatOption[];
  disabled: boolean;
  onSelect: (option: ChatOption) => void;
}

/** Quick-reply buttons returned by the backend for the latest assistant message. */
export default function QuickReplies({ options, disabled, onSelect }: Props) {
  if (!options.length) return null;
  return (
    <div className="flex flex-wrap gap-2 ps-1" role="group" aria-label="Quick replies">
      {options.map((option) => {
        const isHome = option.id === "nav:home";
        return (
          <button
            key={option.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(option)}
            dir="auto"
            className={
              isHome
                ? "inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-3.5 py-1.5 text-sm font-medium text-ink-2 transition-colors hover:bg-canvas disabled:opacity-50"
                : "rounded-full border border-brand-200 bg-surface px-3.5 py-1.5 text-sm font-medium text-brand-700 transition-colors hover:border-brand-500 hover:bg-brand-50 disabled:opacity-50"
            }
          >
            {isHome && <HomeIcon width={14} height={14} />}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
