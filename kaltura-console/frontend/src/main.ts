import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import { useSession } from "./session";
import { toast } from "./api";
import App from "./App.vue";
import Login from "./views/Login.vue";
import Dashboard from "./views/Dashboard.vue";
import Library from "./views/Library.vue";
import Upload from "./views/Upload.vue";
import Detail from "./views/Detail.vue";
import Users from "./views/Users.vue";
import Health from "./views/Health.vue";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "./style.css";
const app = createApp(App);
app.use(createPinia());
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    {
      path: "/login",
      component: Login,
      meta: {
        help: "Use seu e-mail e senha locais. Contate o administrador para obter acesso.",
      },
    },
    {
      path: "/dashboard",
      component: Dashboard,
      meta: { help: "Gerencie os vídeos do seu partner Kaltura." },
    },
    {
      path: "/media",
      component: Library,
      meta: {
        help: "Pesquise por nome. Apenas administradores podem modificar os vídeos.",
      },
    },
    {
      path: "/media/upload",
      component: Upload,
      meta: {
        admin: true,
        help: "Envie um MP4. Aguarde as etapas de envio e processamento.",
      },
    },
    {
      path: "/media/:id",
      component: Detail,
      meta: {
        help: "A reprodução passa pelo console. O status é atualizado a cada 5 segundos.",
      },
    },
    {
      path: "/users",
      component: Users,
      meta: {
        admin: true,
        help: "Gerencie contas locais. O último administrador não pode ser removido.",
      },
    },
    {
      path: "/system/health",
      component: Health,
      meta: { help: "Os testes são independentes e não exibem segredos." },
    },
    { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
  ],
});
router.beforeEach(async (to) => {
  const session = useSession();
  if (!session.loaded) {
    try {
      await session.load();
    } catch (e) {
      toast(String(e));
    }
  }
  if (to.path != "/login" && !session.data)
    return { path: "/login", query: { return: to.fullPath } };
  if (to.meta.admin && !session.admin) return "/dashboard";
});
window.addEventListener("session-expired", () => {
  useSession().data = null;
  if (router.currentRoute.value.path !== "/login")
    void router.push({
      path: "/login",
      query: { return: router.currentRoute.value.fullPath },
    });
});
app.use(router).mount("#app");
