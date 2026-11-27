/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  /** WhatsApp number of the bot, international format, digits only (e.g. 923001234567). */
  readonly VITE_WHATSAPP_NUMBER?: string;
}
