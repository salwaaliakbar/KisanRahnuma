// Mirrors backend/app/schemas/dashboard.py and admin.py. Keep in sync with the FastAPI response models.

export interface ServiceUsage {
  service: string;
  label: string;
  count: number;
}

export interface ServiceFeedback {
  service: string;
  label: string;
  helpful: number;
  not_helpful: number;
}

export interface FeedbackStats {
  helpful: number;
  not_helpful: number;
  by_service: ServiceFeedback[];
}

export interface ConsentStats {
  usage_allowed: number;
  usage_declined: number;
  usage_pending: number;
  weekly_opt_in: number;
  weekly_opt_out: number;
}

export interface RecentInteraction {
  id: string;
  farmer_ref: string;
  service: string;
  service_label: string;
  description: string;
  created_at: string;
}

export interface DashboardSummary {
  window_days: number;
  total_farmers: number;
  new_farmers: number;
  active_farmers: number;
  service_usage: ServiceUsage[];
  feedback: FeedbackStats;
  consent: ConsentStats;
  recent_interactions: RecentInteraction[];
}

export interface MessageUsage {
  month: string;
  sent_by_channel: Record<string, number>;
  whatsapp_sent: number;
  whatsapp_free_limit: number;
  whatsapp_free_remaining: number;
}

export interface FarmerListItem {
  farmer_id: string;
  channel: string;
  language: string;
  district: string | null;
  usage_consent: boolean | null;
  weekly_updates: boolean | null;
  created_at: string;
  updated_at: string;
}

export interface FarmerPage {
  items: FarmerListItem[];
  total: number;
  offset: number;
  limit: number;
}
