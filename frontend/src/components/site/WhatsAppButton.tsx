import { Link } from "react-router-dom";

import { CHAT_FALLBACK, WHATSAPP_URL } from "../../lib/whatsapp";
import { WhatsAppIcon } from "../icons";

type Props = {
  label?: string;
  size?: "md" | "lg";
  className?: string;
};

/** Opens the bot on WhatsApp, or the web chat simulator while no WhatsApp number is configured. */
export default function WhatsAppButton({ label = "Chat on WhatsApp", size = "md", className = "" }: Props) {
  const cls = `inline-flex items-center justify-center gap-2 rounded-full bg-whatsapp font-semibold text-brand-950 shadow-sm transition hover:bg-[#1fbf5b] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-whatsapp-dark ${
    size === "lg" ? "px-6 py-3.5 text-base" : "px-4 py-2 text-sm"
  } ${className}`;
  const icon = <WhatsAppIcon width={size === "lg" ? 22 : 18} height={size === "lg" ? 22 : 18} />;

  if (WHATSAPP_URL) {
    return (
      <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className={cls}>
        {icon}
        {label}
      </a>
    );
  }
  return (
    <Link to={CHAT_FALLBACK} className={cls} title="WhatsApp is launching soon. Opens the web version of the chatbot.">
      {icon}
      {label}
    </Link>
  );
}

/** Round button pinned to the bottom-right corner of every website page. */
export function FloatingWhatsApp() {
  const cls =
    "fixed bottom-5 right-5 z-30 grid h-14 w-14 place-items-center rounded-full bg-whatsapp text-white shadow-lg shadow-brand-950/20 transition hover:scale-105 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-whatsapp-dark";
  const icon = <WhatsAppIcon width={30} height={30} />;
  return WHATSAPP_URL ? (
    <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className={cls} aria-label="Chat with KisanRahnuma on WhatsApp">
      {icon}
    </a>
  ) : (
    <Link to={CHAT_FALLBACK} className={cls} aria-label="Chat with KisanRahnuma">
      {icon}
    </Link>
  );
}
