import axios, { AxiosError } from "axios";

import { clearAdminToken, getAdminToken } from "../lib/adminAuth";
import type { DashboardSummary, FarmerPage, MessageUsage } from "../types/admin";
import { API_BASE_URL } from "./client";

const adminApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

adminApi.interceptors.request.use((config) => {
  const token = getAdminToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

adminApi.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (error instanceof AxiosError && error.response?.status === 401) clearAdminToken();
    return Promise.reject(error);
  },
);

export async function adminLogin(password: string): Promise<{ token: string; expires_at: number }> {
  const { data } = await adminApi.post("/api/admin/login", { password });
  return data;
}

export async function getSummary(days = 7): Promise<DashboardSummary> {
  const { data } = await adminApi.get<DashboardSummary>("/api/dashboard/summary", { params: { days } });
  return data;
}

export async function getMessageUsage(): Promise<MessageUsage> {
  const { data } = await adminApi.get<MessageUsage>("/api/dashboard/messages");
  return data;
}

export async function getFarmers(offset = 0, limit = 20): Promise<FarmerPage> {
  const { data } = await adminApi.get<FarmerPage>("/api/admin/farmers", { params: { offset, limit } });
  return data;
}

export async function getContent(filename: string): Promise<unknown> {
  const { data } = await adminApi.get<{ content: unknown }>(`/api/admin/content/${filename}`);
  return data.content;
}

export async function saveContent(filename: string, content: unknown): Promise<unknown> {
  const { data } = await adminApi.put<{ content: unknown }>(`/api/admin/content/${filename}`, { content });
  return data.content;
}
