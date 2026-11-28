import axios, { AxiosError } from "axios";

import type {
  ChatRequest,
  ChatResponse,
  ConsentStatus,
  FeedbackRequest,
} from "../types/api";

/**
 * Backend URL from frontend/.env: VITE_APP_ENV picks VITE_BACKEND_DEV or VITE_BACKEND_PROD
 * (empty = dev server -> development, build -> production). The defaults here are only a
 * fallback, e.g. on Vercel where the gitignored .env file does not exist.
 */
const env = import.meta.env;
const isProduction = (env.VITE_APP_ENV || (env.PROD ? "production" : "development")) === "production";
const API_BASE_URL = isProduction
  ? env.VITE_BACKEND_PROD || "https://kisanrahnuma.onrender.com"
  : env.VITE_BACKEND_DEV || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

/** Turns any Axios/network error into a short, user-facing message. */
export function errorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    if (!err.response) return `Cannot reach the server at ${API_BASE_URL}. Please try again.`;
    const detail = (err.response.data as { detail?: unknown })?.detail;
    if (typeof detail === "string") return detail;
    if (err.response.status === 422) return "The request was not valid.";
    return `Server error (${err.response.status}).`;
  }
  return "Something went wrong.";
}

export async function sendChat(body: ChatRequest): Promise<ChatResponse> {
  const { data } = await api.post<ChatResponse>("/api/chat", body);
  return data;
}

export async function getConsent(clientId: string): Promise<ConsentStatus | null> {
  try {
    const { data } = await api.get<ConsentStatus>(`/api/consent/${clientId}`);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.status === 404) return null;
    throw err;
  }
}

export async function sendFeedback(body: FeedbackRequest): Promise<void> {
  await api.post("/api/feedback", body);
}
