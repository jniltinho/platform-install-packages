// The server injects a canonical base into index.html; one build works at any prefix.
export function basePath(): string {
  if (typeof document === "undefined") return "";
  const href = document.querySelector("base")?.getAttribute("href") ?? "/";
  return href.replace(/\/$/, "");
}
export function apiPath(path: string): string {
  return basePath() + "/api" + path;
}
