/**
 * WhatsApp click-to-chat link for the KisanRahnuma bot.
 *
 * Set VITE_WHATSAPP_NUMBER in frontend/.env to the bot's number in international format,
 * digits only (e.g. 923001234567). Until it is set, "Chat on WhatsApp" opens the web chat
 * simulator instead, which runs the same conversation engine.
 */
const number = (import.meta.env.VITE_WHATSAPP_NUMBER ?? "").replace(/\D/g, "");

export const WHATSAPP_ENABLED = number.length >= 8;

/** Opens WhatsApp with "Hi" pre-filled, which starts the bot's welcome flow. */
export const WHATSAPP_URL = WHATSAPP_ENABLED ? `https://wa.me/${number}?text=${encodeURIComponent("Hi")}` : null;

/** The route used when WhatsApp is not configured yet. */
export const CHAT_FALLBACK = "/chat";
