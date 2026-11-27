import { LANGUAGES, type Language } from "../../lib/i18n";

interface Props {
  value: Language;
  label: string;
  disabled: boolean;
  onChange: (code: Language) => void;
}

/** English / اردو / سنڌي toggle. Each choice is sent to the backend as a chat message (lang:<code>). */
export default function LanguageSwitcher({ value, label, disabled, onChange }: Props) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-full border border-line bg-canvas p-0.5">
      {LANGUAGES.map(({ code, name, dir }) => {
        const active = code === value;
        return (
          <button
            key={code}
            type="button"
            role="radio"
            aria-checked={active}
            lang={code}
            dir={dir}
            disabled={disabled}
            onClick={() => !active && onChange(code)}
            className={`rounded-full px-3 py-1 text-sm font-medium transition-colors disabled:opacity-50 ${
              active ? "bg-surface text-brand-700 shadow-sm" : "text-ink-2 hover:text-ink"
            }`}
          >
            {code === "en" ? "EN" : name}
          </button>
        );
      })}
    </div>
  );
}
