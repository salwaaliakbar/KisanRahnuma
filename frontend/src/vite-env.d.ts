/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** "development" or "production"; empty = from the Vite mode (dev server vs build). */
  readonly VITE_APP_ENV?: string;
  readonly VITE_BACKEND_DEV?: string;
  readonly VITE_BACKEND_PROD?: string;
  /** WhatsApp number of the bot, international format, digits only (e.g. 923001234567). */
  readonly VITE_WHATSAPP_NUMBER?: string;
}
