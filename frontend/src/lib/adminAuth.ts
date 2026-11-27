// Admin login token: one shared operator password, not per-farmer identity. Stored the
// same way the farmer's anonymous client_id is (see storage.ts), scoped to its own key.
import { readStorage, removeStorage, writeStorage } from "./storage";

const TOKEN_KEY = "kr_admin_token";

export function getAdminToken(): string | null {
  return readStorage<string | null>("local", TOKEN_KEY, null);
}

export function setAdminToken(token: string): void {
  writeStorage("local", TOKEN_KEY, token);
}

export function clearAdminToken(): void {
  removeStorage("local", TOKEN_KEY);
}
