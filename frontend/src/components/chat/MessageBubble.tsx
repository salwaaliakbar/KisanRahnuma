import type { ChatItem } from "../../hooks/useChat";
import { formatTime, RichText } from "../../lib/format";
import type { UIStrings } from "../../lib/i18n";
import type { BotMessage } from "../../types/api";
import { MicIcon } from "../icons";
import FeedbackBar from "./FeedbackBar";

interface Props {
  item: ChatItem;
  ui: UIStrings;
  onFeedback: (message: BotMessage, helpful: boolean) => void;
}

export default function MessageBubble({ item, ui, onFeedback }: Props) {
  if (item.kind === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-ee-md bg-bubble-user px-3.5 py-2 text-[15px] leading-relaxed text-ink shadow-[0_1px_0_rgba(0,0,0,0.04)] sm:max-w-[70%]">
          {item.voice ? (
            <VoiceNote label={ui.voiceNote} />
          ) : (
            <span dir="auto" className="block whitespace-pre-wrap break-words">
              {item.text}
            </span>
          )}
          <div className="mt-0.5 text-end text-[11px] text-ink-3">{formatTime(item.at)}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] rounded-2xl rounded-es-md border border-line bg-surface px-3.5 py-2.5 text-[15px] leading-relaxed text-ink shadow-[0_1px_0_rgba(0,0,0,0.03)] sm:max-w-[75%]">
        <div dir="auto" className="break-words">
          <RichText text={item.text} />
        </div>
        <div className="mt-1 text-end text-[11px] text-ink-3">{formatTime(item.at)}</div>
        {item.feedback && <FeedbackBar ui={ui} state={item.feedbackState} onVote={(helpful) => onFeedback(item, helpful)} />}
      </div>
    </div>
  );
}

function VoiceNote({ label }: { label: string }) {
  const bars = [6, 12, 9, 16, 7, 13, 18, 10, 6, 14, 9, 12, 7, 5];
  return (
    <span className="flex items-center gap-2.5 py-0.5" aria-label={label}>
      <span className="grid h-8 w-8 place-items-center rounded-full bg-brand-600 text-white">
        <MicIcon width={16} height={16} />
      </span>
      <span className="flex items-center gap-[3px]" aria-hidden>
        {bars.map((h, i) => (
          <span key={i} className="w-[3px] rounded-full bg-brand-700/60" style={{ height: h }} />
        ))}
      </span>
      <span className="text-xs text-ink-2">0:04</span>
    </span>
  );
}
