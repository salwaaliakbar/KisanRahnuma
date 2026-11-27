// Browser storage can be unavailable (private mode, blocked site data) - never let it crash the app.

export function readStorage<T>(store: "local" | "session", key: string, fallback: T): T {
  try {
    const raw = (store === "local" ? localStorage : sessionStorage).getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

export function writeStorage(store: "local" | "session", key: string, value: unknown): void {
  try {
    (store === "local" ? localStorage : sessionStorage).setItem(key, JSON.stringify(value));
  } catch {
    /* ignore */
  }
}

export function removeStorage(store: "local" | "session", key: string): void {
  try {
    (store === "local" ? localStorage : sessionStorage).removeItem(key);
  } catch {
    /* ignore */
  }
}

export function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  // Fallback for older browsers / non-secure contexts.
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) =>
    (Number(c) ^ (Math.random() * 16) >> (Number(c) / 4)).toString(16),
  );
}
