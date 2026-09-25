export interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "viewer";
}
export interface Session {
  user: User;
  csrf: string;
  partner_id: number;
  version: string;
}
export interface Entry {
  id: string;
  name: string;
  description: string;
  status: number;
  status_label: string;
  status_group: string;
  duration: number;
  created_at: number;
  width: number;
  height: number;
  thumbnail_url: string;
  playback_url: string;
}
export interface Page {
  items: Entry[];
  total: number;
  page: number;
  pages: number;
}
export interface Flavor {
  id: string;
  type: string;
  status_label: string;
  status_group: string;
  width: number;
  height: number;
  size_kb: number;
  bitrate: number;
  format: string;
}
export interface HealthCheck {
  group: string;
  name: string;
  ok: boolean;
  detail: string;
}
