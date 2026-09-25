<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Film,
  LogOut,
  Activity,
  Users,
  LayoutDashboard,
} from "lucide-vue-next";
import { useSession } from "./session";
import { notice, toast } from "./api";
import { t, locale, changeLocale } from "./i18n";
const session = useSession(),
  route = useRoute(),
  router = useRouter();
const media = computed(() => route.path.startsWith("/media"));
async function logout() {
  try {
    await session.logout();
    await router.push("/login");
  } catch (e) {
    toast(String(e));
  }
}
</script>
<template>
  <div class="shell">
    <header>
      <div class="brand">
        <Film :size="28" />
        <div>
          KALTURA <strong>CONSOLE</strong><small>Media management</small>
        </div>
      </div>
      <select
        aria-label="Language"
        :value="locale"
        @change="changeLocale(($event.target as HTMLSelectElement).value)"
      >
        <option value="pt-BR">Português</option>
        <option value="en">English</option>
      </select>
    </header>
    <nav v-if="session.data" class="tabs" aria-label="Main">
      <RouterLink to="/dashboard"
        ><LayoutDashboard :size="16" />{{ t("Painel") }}</RouterLink
      >
      <RouterLink to="/media" :class="{ active: media }"
        ><Film :size="16" />{{ t("Mídia") }}</RouterLink
      >
      <RouterLink v-if="session.admin" to="/users"
        ><Users :size="16" />{{ t("Usuários") }}</RouterLink
      >
      <RouterLink to="/system/health"
        ><Activity :size="16" />{{ t("Saúde do sistema") }}</RouterLink
      >
      <button @click="logout"><LogOut :size="16" />{{ t("Sair") }}</button>
    </nav>
    <nav class="submenu">
      <template v-if="media && session.data"
        ><RouterLink to="/media">{{ t("Biblioteca") }}</RouterLink
        ><RouterLink v-if="session.admin" to="/media/upload">{{
          t("Upload")
        }}</RouterLink></template
      >
    </nav>
    <div v-if="session.data" class="infobar">
      <span
        >Partner: <b>{{ session.data.partner_id }}</b></span
      ><span
        ><b>{{ session.data.user.name }}</b> ·
        {{ session.data.user.role }}</span
      >
    </div>
    <div class="layout">
      <main>
        <div class="content"><RouterView :key="route.path" /></div>
        <footer>
          Kaltura Console · {{ session.data?.version ?? "Go + Vue" }}
        </footer>
      </main>
      <aside>
        <h2>{{ t("Ajuda") }}</h2>
        <p>{{ t(String(route.meta.help ?? "")) }}</p>
      </aside>
    </div>
  </div>
  <div v-if="notice" role="alert" class="toast">
    {{ notice }}<button aria-label="Close" @click="notice = ''">×</button>
  </div>
</template>
