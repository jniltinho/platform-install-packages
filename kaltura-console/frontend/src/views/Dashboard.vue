<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, toast } from "../api";
import { t } from "../i18n";
import type { Entry } from "../types";
import Entries from "../components/Entries.vue";
const data = ref<{ counts: Record<string, number>; recent: Entry[] } | null>(
  null,
);
const labels: Record<string, string> = {
  total: "Total",
  ready: "Pronto",
  processing: "Processando",
  error: "Erro",
};
onMounted(async () => {
  try {
    data.value = await api("/dashboard");
  } catch (e) {
    toast(String(e));
  }
});
</script>
<template>
  <h1>{{ t("Painel") }}</h1>
  <template v-if="data"
    ><div class="stats">
      <div v-for="(label, key) in labels" :key="key" class="stat">
        {{ t(label) }}<strong>{{ data.counts[key] }}</strong>
      </div>
    </div>
    <h2>{{ t("Recentes") }}</h2>
    <Entries :items="data.recent"
  /></template>
  <p v-else>{{ t("Carregando…") }}</p>
</template>
