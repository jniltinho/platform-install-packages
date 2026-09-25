<script setup lang="ts">
import type { Entry } from "../types";
import { t, locale } from "../i18n";
import { duration } from "../api";
defineProps<{ items: Entry[] }>();
</script>
<template>
  <div class="table-scroll">
    <table>
      <thead>
        <tr>
          <th></th>
          <th>{{ t("Nome") }}</th>
          <th>{{ t("Status") }}</th>
          <th>{{ t("Duração") }}</th>
          <th>{{ t("Criado em") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="e in items" :key="e.id">
          <td><img :src="e.thumbnail_url" alt="" loading="lazy" /></td>
          <td>
            <RouterLink class="entry-name" :to="'/media/' + e.id">{{
              e.name
            }}</RouterLink
            ><small class="muted">{{ e.id }}</small>
          </td>
          <td>
            <span class="badge" :class="e.status_group">{{
              t(e.status_label)
            }}</span>
          </td>
          <td>{{ duration(e.duration) }}</td>
          <td>
            {{ new Date(e.created_at * 1000).toLocaleDateString(locale) }}
          </td>
        </tr>
        <tr v-if="!items.length">
          <td colspan="5">{{ t("Nenhum resultado") }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
