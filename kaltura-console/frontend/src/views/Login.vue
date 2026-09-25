<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useSession } from "../session";
import { safeReturn, toast } from "../api";
import { t } from "../i18n";
const email = ref(""),
  password = ref(""),
  remember = ref(false),
  busy = ref(false);
const session = useSession(),
  router = useRouter(),
  route = useRoute();
async function submit() {
  busy.value = true;
  try {
    await session.login(email.value, password.value, remember.value);
    await router.push(safeReturn(route.query.return));
  } catch (e) {
    toast(String(e));
  } finally {
    busy.value = false;
    password.value = "";
  }
}
</script>
<template>
  <form class="login" @submit.prevent="submit">
    <h1>{{ t("Entrar") }}</h1>
    <label
      >{{ t("E-mail")
      }}<input
        v-model="email"
        type="email"
        autocomplete="username"
        required /></label
    ><label
      >{{ t("Senha")
      }}<input
        v-model="password"
        type="password"
        autocomplete="current-password"
        required /></label
    ><label class="check"
      ><input v-model="remember" type="checkbox" />{{ t("Lembrar-me") }}</label
    ><button :disabled="busy">{{ t("Entrar") }}</button>
  </form>
</template>
