import axios, { AxiosError } from "axios";

import type {
  ChatRequest,
  ChatResponse,
  ConsentStatus,
  FeedbackRequest,
} from "../types/api";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

/** Turns any Axios/network error into a short, user-facing message. */
export function errorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    if (!err.response) return "Cannot reach the server. Is the backend running on port 8000?";
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
