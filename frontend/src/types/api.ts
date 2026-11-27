// Mirrors backend/app/schemas. Keep in sync with the FastAPI response models.

export interface ChatOption {
  id: string;
  label: string;
}

export interface BotMessage {
  id: string;
  text: string;
  options: ChatOption[];
  feedback: boolean;
  service: string | null;
}

export interface ChatRequest {
  client_id: string;
  text?: string;
  option_id?: string;
  message_type?: "text" | "voice";
}

export interface ChatResponse {
  farmer_id: string;
  session_id: string;
  state: string;
  language: "en" | "ur" | "sd";
  messages: BotMessage[];
}

export interface ConsentStatus {
  farmer_id: string;
  usage_consent: boolean | null;
  usage_consent_at: string | null;
  weekly_updates: boolean | null;
  weekly_updates_at: string | null;
}

export interface FeedbackRequest {
  client_id: string;
  response_id: string;
  service: string;
  helpful: boolean;
}
