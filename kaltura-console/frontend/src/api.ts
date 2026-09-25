import { apiPath } from "./base";
import { ref } from "vue";
export const notice = ref("");
let noticeTimer: ReturnType<typeof setTimeout> | undefined;
export function toast(message: string) {
  notice.value = message;
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => (notice.value = ""), 7000);
}
export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
  csrf = "",
): Promise<T> {
  const response = await fetch(apiPath(path), {
    method,
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    if (
      response.status === 401 &&
      path !== "/login" &&
      typeof window !== "undefined"
    )
      window.dispatchEvent(new Event("session-expired"));
    const data = await response
      .json()
      .catch(() => ({ message: response.statusText }));
    throw new APIError(response.status, data.message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
export function safeReturn(raw: unknown): string {
  if (
    typeof raw !== "string" ||
    !raw.startsWith("/") ||
    raw.startsWith("//") ||
    raw.includes("\\") ||
    [...raw].some((c) => c.charCodeAt(0) < 32) ||
    raw.startsWith("/login")
  )
    return "/dashboard";
  try {
    const url = new URL(raw, "https://console.invalid");
    return url.origin === "https://console.invalid"
      ? url.pathname + url.search + url.hash
      : "/dashboard";
  } catch {
    return "/dashboard";
  }
}
export function duration(seconds: number) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}
