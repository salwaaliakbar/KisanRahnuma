import { useCallback, useEffect, useRef, useState } from "react";

import { errorMessage, getConsent, sendChat, sendFeedback } from "../api/client";
import { isLanguage, languageInfo, uiStrings, type Language } from "../lib/i18n";
import { newId, readStorage, removeStorage, writeStorage } from "../lib/storage";
import type { BotMessage, ChatRequest, ConsentStatus } from "../types/api";

export type FeedbackState = "sending" | "yes" | "no" | "error";

export type ChatItem =
  | { kind: "user"; id: string; text: string; voice?: boolean; at: string }
  | ({ kind: "bot"; at: string; feedbackState?: FeedbackState } & BotMessage);

export interface Outgoing {
  text?: string;
  optionId?: string;
  label?: string; // what the farmer "sees" they sent (button label)
  voice?: boolean;
}

const CLIENT_KEY = "fa.clientId";
const historyKey = (clientId: string) => `fa.history.${clientId}`;
const languageKey = (clientId: string) => `fa.language.${clientId}`;

/**
 * Chat state for the simulator. It only sends messages and renders what the backend
 * returns - every reply and next step is decided by the backend conversation engine.
 */
export function useChat() {
  const [clientId, setClientId] = useState<string>(() => {
    const existing = readStorage<string | null>("local", CLIENT_KEY, null);
    if (existing) return existing;
    const id = newId();
    writeStorage("local", CLIENT_KEY, id);
    return id;
  });
  const [items, setItems] = useState<ChatItem[]>(() => readStorage("session", historyKey(clientId), []));
  const [state, setState] = useState<string | null>(null);
  // The farmer's language as last reported by the backend (drives RTL and UI strings).
  const [language, setLanguage] = useState<Language>(() => {
    const saved = readStorage<string>("local", languageKey(clientId), "en");
    return isLanguage(saved) ? saved : "en";
  });
  const [consent, setConsent] = useState<ConsentStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastRequest = useRef<ChatRequest | null>(null);

  useEffect(() => writeStorage("session", historyKey(clientId), items), [clientId, items]);
  useEffect(() => writeStorage("local", languageKey(clientId), language), [clientId, language]);

  const refreshConsent = useCallback(async (id: string) => {
    try {
      setConsent(await getConsent(id));
    } catch {
      /* side panel only; ignore */
    }
  }, []);

  useEffect(() => {
    void refreshConsent(clientId);
  }, [clientId, refreshConsent]);

  const post = useCallback(
    async (request: ChatRequest) => {
      lastRequest.current = request;
      setLoading(true);
      setError(null);
      try {
        const res = await sendChat(request);
        const at = new Date().toISOString();
        setItems((prev) => [...prev, ...res.messages.map((m) => ({ ...m, kind: "bot" as const, at }))]);
        setState(res.state);
        if (isLanguage(res.language)) setLanguage(res.language);
        void refreshConsent(request.client_id);
      } catch (err) {
        setError(errorMessage(err));
      } finally {
        setLoading(false);
      }
    },
    [refreshConsent],
  );

  const send = useCallback(
    (msg: Outgoing) => {
      const shown = msg.voice ? uiStrings(language).voiceNote : (msg.label ?? msg.text ?? "").trim();
      if (!msg.voice && !shown) return;
      setItems((prev) => [
        ...prev,
        { kind: "user", id: newId(), text: shown, voice: msg.voice, at: new Date().toISOString() },
      ]);
      void post({
        client_id: clientId,
        text: msg.voice ? undefined : (msg.text ?? msg.label),
        option_id: msg.optionId,
        message_type: msg.voice ? "voice" : "text",
      });
    },
    [clientId, language, post],
  );

  /** Switch language the same way a WhatsApp farmer would: by sending a language choice. */
  const changeLanguage = useCallback(
    (code: Language) => {
      const { name } = languageInfo(code);
      send({ text: name, optionId: `lang:${code}`, label: name });
    },
    [send],
  );

  const retry = useCallback(() => {
    if (lastRequest.current) void post(lastRequest.current);
  }, [post]);

  const giveFeedback = useCallback(
    async (message: BotMessage, helpful: boolean) => {
      const update = (feedbackState: FeedbackState) =>
        setItems((prev) => prev.map((it) => (it.kind === "bot" && it.id === message.id ? { ...it, feedbackState } : it)));
      update("sending");
      try {
        await sendFeedback({
          client_id: clientId,
          response_id: message.id,
          service: message.service ?? "unknown",
          helpful,
        });
        update(helpful ? "yes" : "no");
      } catch {
        update("error");
      }
    },
    [clientId],
  );

  const startNewFarmer = useCallback(() => {
    removeStorage("session", historyKey(clientId));
    removeStorage("local", languageKey(clientId));
    const id = newId();
    writeStorage("local", CLIENT_KEY, id);
    setClientId(id);
    setItems([]);
    setState(null);
    setConsent(null);
    setLanguage("en");
    setError(null);
  }, [clientId]);

  return {
    clientId,
    items,
    state,
    language,
    consent,
    loading,
    error,
    send,
    changeLanguage,
    retry,
    giveFeedback,
    startNewFarmer,
  };
}
