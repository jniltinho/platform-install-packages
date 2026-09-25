<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, toast } from "../api";
import { useSession } from "../session";
import { t } from "../i18n";
import type { Page } from "../types";
import Entries from "../components/Entries.vue";
const data = ref<Page | null>(null),
  query = ref(""),
  busy = ref(false),
  session = useSession();
async function load(page = 1) {
  busy.value = true;
  try {
    data.value = await api(
      `/media?page=${page}&q=${encodeURIComponent(query.value)}`,
    );
  } catch (e) {
    toast(String(e));
  } finally {
    busy.value = false;
  }
}
onMounted(() => load());
</script>
<template>
  <h1>{{ t("Biblioteca") }}</h1>
  <form class="search" @submit.prevent="load()">
    <input v-model="query" :aria-label="t('Buscar')" maxlength="100" /><button
      :disabled="busy"
    >
      {{ t("Buscar") }}</button
    ><RouterLink
      v-if="session.admin"
      class="button secondary"
      to="/media/upload"
      >{{ t("Upload") }}</RouterLink
    >
  </form>
  <template v-if="data"
    ><Entries :items="data.items" />
    <div class="pagination">
      <button :disabled="busy || data.page <= 1" @click="load(data.page - 1)">
        {{ t("Anterior") }}</button
      ><span>{{ data.page }} / {{ data.pages }} · {{ data.total }}</span
      ><button
        :disabled="busy || data.page >= data.pages"
        @click="load(data.page + 1)"
      >
        {{ t("Próxima") }}
      </button>
    </div></template
  >
</template>
