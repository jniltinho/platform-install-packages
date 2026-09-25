<script setup lang="ts">
import { ref, onMounted } from "vue";
import { api, toast } from "../api";
import { t } from "../i18n";
import { useSession } from "../session";
import type { User } from "../types";
const users = ref<User[]>([]),
  name = ref(""),
  email = ref(""),
  password = ref(""),
  role = ref("viewer"),
  busy = ref(false),
  session = useSession();
async function load() {
  try {
    users.value = await api("/users");
  } catch (e) {
    toast(String(e));
  }
}
async function create() {
  await change("/users", "POST", {
    name: name.value,
    email: email.value,
    password: password.value,
    role: role.value,
  });
  password.value = "";
}
async function change(path: string, method: string, body?: unknown) {
  busy.value = true;
  try {
    await api(path, method, body, session.data?.csrf);
    toast(t("Operação concluída"));
    await load();
  } catch (e) {
    toast(String(e));
  } finally {
    busy.value = false;
  }
}
const resetUser = ref<User | null>(null),
  newPassword = ref("");
function reset(user: User) {
  resetUser.value = user;
  newPassword.value = "";
}
async function savePassword() {
  if (!resetUser.value) return;
  await change("/users/" + resetUser.value.id, "PATCH", {
    password: newPassword.value,
  });
  newPassword.value = "";
  resetUser.value = null;
}
function remove(user: User) {
  if (confirm(t("Confirmar exclusão?")))
    void change("/users/" + user.id, "DELETE");
}
onMounted(load);
</script>
<template>
  <h1>{{ t("Usuários") }}</h1>
  <div class="table-scroll">
    <table>
      <thead>
        <tr>
          <th>{{ t("Nome") }}</th>
          <th>{{ t("E-mail") }}</th>
          <th>{{ t("Papel") }}</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.name }}</td>
          <td>{{ u.email }}</td>
          <td>
            <select
              :aria-label="t('Papel') + ' ' + u.email"
              :value="u.role"
              :disabled="busy"
              @change="
                change('/users/' + u.id, 'PATCH', {
                  role: ($event.target as HTMLSelectElement).value,
                })
              "
            >
              <option value="admin">{{ t("Administrador") }}</option>
              <option value="viewer">{{ t("Visualizador") }}</option>
            </select>
          </td>
          <td>
            <div class="actions">
              <button :disabled="busy" @click="reset(u)">
                {{ t("Redefinir senha") }}</button
              ><button
                class="danger"
                :disabled="busy || u.id === session.data?.user.id"
                @click="remove(u)"
              >
                {{ t("Excluir") }}
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <form v-if="resetUser" class="section" @submit.prevent="savePassword">
    <h2>{{ t("Redefinir senha") }}: {{ resetUser.email }}</h2>
    <label
      >{{ t("Senha")
      }}<input
        v-model="newPassword"
        type="password"
        minlength="8"
        maxlength="72"
        autocomplete="new-password"
        required
    /></label>
    <div class="actions">
      <button :disabled="busy">{{ t("Salvar") }}</button
      ><button type="button" class="secondary" @click="resetUser = null">
        {{ t("Cancelar") }}
      </button>
    </div>
  </form>
  <h2>{{ t("Adicionar usuário") }}</h2>
  <form @submit.prevent="create">
    <label
      >{{ t("Nome") }}<input v-model="name" maxlength="255" required /></label
    ><label
      >{{ t("E-mail")
      }}<input v-model="email" type="email" maxlength="254" required /></label
    ><label
      >{{ t("Senha")
      }}<input
        v-model="password"
        type="password"
        minlength="8"
        maxlength="72"
        autocomplete="new-password"
        required /></label
    ><label
      >{{ t("Papel")
      }}<select v-model="role">
        <option value="viewer">{{ t("Visualizador") }}</option>
        <option value="admin">{{ t("Administrador") }}</option>
      </select></label
    ><button :disabled="busy">{{ t("Adicionar usuário") }}</button>
  </form>
</template>
