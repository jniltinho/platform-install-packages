<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, toast } from "../api";
import { t } from "../i18n";
import type { HealthCheck } from "../types";
const checks = ref<HealthCheck[]>([]),
  busy = ref(false);
async function load() {
  busy.value = true;
  try {
    checks.value = await api("/health");
  } catch (e) {
    toast(String(e));
  } finally {
    busy.value = false;
  }
}
onMounted(load);
</script>
<template>
  <h1>{{ t("Saúde do sistema") }}</h1>
  <div class="actions">
    <button :disabled="busy" @click="load">{{ t("Atualizar") }}</button
    ><span v-if="busy">{{ t("Carregando…") }}</span>
  </div>
  <div class="table-scroll">
    <table>
      <thead>
        <tr>
          <th>{{ t("Nome") }}</th>
          <th>{{ t("Status") }}</th>
          <th>{{ t("Descrição") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in checks" :key="c.name">
          <td>{{ c.group }} · {{ t(c.name) }}</td>
          <td>
            <span class="badge" :class="c.ok ? 'ready' : 'error'">{{
              c.ok ? "OK" : t("Erro")
            }}</span>
          </td>
          <td>{{ t(c.detail) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
