import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api, APIError } from "./api";
import type { Session } from "./types";
export const useSession = defineStore("session", () => {
  const data = ref<Session | null>(null);
  const loaded = ref(false);
  const admin = computed(() => data.value?.user.role === "admin");
  async function load() {
    try {
      data.value = await api<Session>("/session");
    } catch (e) {
      if (!(e instanceof APIError && e.status === 401)) throw e;
      data.value = null;
    } finally {
      loaded.value = true;
    }
  }
  async function login(email: string, password: string, remember: boolean) {
    data.value = await api<Session>(
      "/login",
      "POST",
      { email, password, remember },
      data.value?.csrf,
    );
    loaded.value = true;
  }
  async function logout() {
    await api("/logout", "POST", undefined, data.value?.csrf);
    data.value = null;
  }
  return { data, loaded, admin, load, login, logout };
});
