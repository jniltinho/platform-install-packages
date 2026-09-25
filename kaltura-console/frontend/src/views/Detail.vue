<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api, toast, duration } from "../api";
import { useSession } from "../session";
import { t, locale } from "../i18n";
import type { Entry, Flavor } from "../types";
const entry = ref<Entry | null>(null),
  flavors = ref<Flavor[]>([]),
  flavorError = ref(false),
  name = ref(""),
  description = ref(""),
  busy = ref(false),
  stopped = ref(false);
const route = useRoute(),
  router = useRouter(),
  session = useSession(),
  id = encodeURIComponent(String(route.params.id));
let timer: ReturnType<typeof setTimeout> | undefined,
  count = 0,
  alive = true;
async function loadFlavors() {
  try {
    flavors.value = await api("/media/" + id + "/flavors");
    flavorError.value = false;
  } catch {
    flavorError.value = true;
  }
}
async function load() {
  try {
    entry.value = await api("/media/" + id);
    name.value = entry.value!.name;
    description.value = entry.value!.description;
    await loadFlavors();
    schedule();
  } catch (e) {
    toast(String(e));
  }
}
function schedule() {
  clearTimeout(timer);
  if (!alive || entry.value?.status_group !== "processing") return;
  if (count >= 240) {
    stopped.value = true;
    return;
  }
  timer = setTimeout(poll, 5000);
}
async function poll() {
  count++;
  try {
    const status = await api<Partial<Entry>>("/media/" + id + "/status");
    if (entry.value) Object.assign(entry.value, status);
    if (entry.value?.status_group === "ready") await loadFlavors();
  } catch (e) {
    toast(String(e));
  }
  schedule();
}
async function save() {
  busy.value = true;
  try {
    entry.value = await api(
      "/media/" + id,
      "PATCH",
      { name: name.value, description: description.value },
      session.data?.csrf,
    );
    toast(t("Operação concluída"));
  } catch (e) {
    toast(String(e));
  } finally {
    busy.value = false;
  }
}
async function remove() {
  if (!confirm(t("Confirmar exclusão?"))) return;
  busy.value = true;
  try {
    await api("/media/" + id, "DELETE", undefined, session.data?.csrf);
    toast(t("Operação concluída"));
    await router.push("/media");
  } catch (e) {
    toast(String(e));
  } finally {
    busy.value = false;
  }
}
onMounted(load);
onBeforeUnmount(() => {
  alive = false;
  clearTimeout(timer);
});
</script>
<template>
  <template v-if="entry"
    ><h1>{{ entry.name }}</h1>
    <video
      v-if="entry.status_group === 'ready'"
      :src="entry.playback_url"
      :poster="entry.thumbnail_url"
      controls
      preload="metadata"
    />
    <div v-else class="section">
      {{
        entry.status_group === "processing"
          ? t("Aguardando processamento no Kaltura")
          : t("Vídeo indisponível")
      }}
      · {{ t(entry.status_label) }}
    </div>
    <p v-if="stopped">
      {{
        t("Consulta automática encerrada. Atualize para consultar novamente.")
      }}
    </p>
    <dl class="details">
      <div>
        <dt>ID</dt>
        <dd>{{ entry.id }}</dd>
      </div>
      <div>
        <dt>{{ t("Status") }}</dt>
        <dd>
          <span class="badge" :class="entry.status_group">{{
            t(entry.status_label)
          }}</span>
        </dd>
      </div>
      <div>
        <dt>{{ t("Duração") }}</dt>
        <dd>{{ duration(entry.duration) }}</dd>
      </div>
      <div>
        <dt>{{ t("Resolução") }}</dt>
        <dd>{{ entry.width }} × {{ entry.height }}</dd>
      </div>
      <div>
        <dt>{{ t("Criado em") }}</dt>
        <dd>{{ new Date(entry.created_at * 1000).toLocaleString(locale) }}</dd>
      </div>
    </dl>
    <form v-if="session.admin" @submit.prevent="save">
      <label
        >{{ t("Nome") }}<input v-model="name" required maxlength="255" /></label
      ><label
        >{{ t("Descrição") }}<textarea v-model="description" maxlength="5000" />
      </label>
      <div class="actions">
        <button :disabled="busy">{{ t("Salvar") }}</button
        ><button type="button" class="danger" :disabled="busy" @click="remove">
          {{ t("Excluir") }}
        </button>
      </div>
    </form>
    <p v-else>{{ entry.description }}</p>
    <h2>Flavors</h2>
    <p v-if="flavorError" role="alert">{{ t("Falha ao carregar flavors") }}</p>
    <div v-else class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>{{ t("Tipo") }}</th>
            <th>{{ t("Status") }}</th>
            <th>{{ t("Resolução") }}</th>
            <th>{{ t("Tamanho") }}</th>
            <th>Bitrate</th>
            <th>{{ t("Formato") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in flavors" :key="f.id">
            <td>{{ f.type }}</td>
            <td>
              <span class="badge" :class="f.status_group">{{
                t(f.status_label)
              }}</span>
            </td>
            <td>{{ f.width }} × {{ f.height }}</td>
            <td>{{ f.size_kb }} KB</td>
            <td>{{ f.bitrate }} kbps</td>
            <td>{{ f.format }}</td>
          </tr>
        </tbody>
      </table>
    </div></template
  >
  <p v-else>{{ t("Carregando…") }}</p>
</template>
