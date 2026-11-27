import { Fragment, type ReactNode } from "react";

/** Renders WhatsApp-style markup (*bold*, _italic_) and line breaks. Display only, no logic. */
export function RichText({ text }: { text: string }) {
  return (
    <>
      {text.split("\n").map((line, i, lines) => (
        <Fragment key={i}>
          {renderInline(line)}
          {i < lines.length - 1 && <br />}
        </Fragment>
      ))}
    </>
  );
}

function renderInline(line: string): ReactNode[] {
  return line.split(/(\*[^*\n]+\*|_[^_\n]+_)/g).map((part, i) => {
    if (part.length > 2 && part.startsWith("*") && part.endsWith("*"))
      return <strong key={i} className="font-semibold">{part.slice(1, -1)}</strong>;
    if (part.length > 2 && part.startsWith("_") && part.endsWith("_"))
      return <em key={i} className="text-ink-2">{part.slice(1, -1)}</em>;
    return part;
  });
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString([], { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export function formatState(state: string): string {
  return state.toLowerCase().replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}
