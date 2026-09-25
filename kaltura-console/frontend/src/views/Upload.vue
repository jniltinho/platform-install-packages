<script setup lang="ts">
import { ref, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useSession } from "../session";
import { toast } from "../api";
import { t } from "../i18n";
const name = ref(""),
  description = ref(""),
  file = ref<File | null>(null),
  busy = ref(false),
  progress = ref(0),
  phase = ref("");
const session = useSession(),
  router = useRouter();
let xhr: XMLHttpRequest | undefined;
function select(event: Event) {
  file.value = (event.target as HTMLInputElement).files?.[0] ?? null;
  if (file.value && !name.value)
    name.value = file.value.name.replace(/\.[^.]+$/, "");
}
function submit() {
  if (!file.value) {
    toast(t("Selecione um arquivo"));
    return;
  }
  busy.value = true;
  progress.value = 0;
  phase.value = "Enviando ao console";
  const body = new FormData();
  body.append("name", name.value);
  body.append("description", description.value);
  body.append("file", file.value);
  xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/media");
  xhr.setRequestHeader("X-CSRF-Token", session.data?.csrf ?? "");
  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable)
      progress.value = Math.round((e.loaded / e.total) * 100);
  };
  xhr.upload.onload = () => {
    progress.value = 100;
    phase.value = "Enviando ao Kaltura";
  };
  xhr.onload = () => {
    busy.value = false;
    try {
      const result = JSON.parse(xhr!.responseText);
      if (xhr!.status !== 201) throw new Error(result.message);
      phase.value = "Processando";
      toast(t("Aguardando processamento no Kaltura"));
      void router.push("/media/" + result.id);
    } catch (e) {
      toast(String(e));
    }
  };
  xhr.onerror = () => {
    busy.value = false;
    toast(t("Erro"));
  };
  xhr.onabort = () => {
    busy.value = false;
  };
  xhr.send(body);
}
onBeforeUnmount(() => xhr?.abort());
</script>
<template>
  <h1>{{ t("Upload") }}</h1>
  <form @submit.prevent="submit">
    <label
      >{{ t("Nome")
      }}<input
        v-model="name"
        required
        maxlength="255"
        :disabled="busy" /></label
    ><label
      >{{ t("Descrição")
      }}<textarea
        v-model="description"
        maxlength="5000"
        :disabled="busy"
      /></label
    ><label
      >{{ t("Arquivo MP4")
      }}<input
        type="file"
        accept=".mp4"
        required
        :disabled="busy"
        @change="select"
    /></label>
    <div v-if="phase" class="section" aria-live="polite">
      {{ t(phase) }} · {{ progress }}%<progress :value="progress" max="100" />
    </div>
    <div class="actions">
      <button :disabled="busy">{{ t("Enviar") }}</button
      ><button
        v-if="busy"
        type="button"
        class="secondary"
        @click="xhr?.abort()"
      >
        {{ t("Cancelar") }}
      </button>
    </div>
  </form>
</template>
