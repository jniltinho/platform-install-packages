import { ref } from "vue";
export const locale = ref(
  localStorage.getItem("locale") === "en" ? "en" : "pt-BR",
);
const en: Record<string, string> = {
  "Erro na importação": "Import error",
  "Erro na conversão": "Conversion error",
  Importando: "Importing",
  Excluído: "Deleted",
  Pendente: "Pending",
  "Em moderação": "Moderated",
  Bloqueado: "Blocked",
  "Sem conteúdo": "No content",
  Desconhecido: "Unknown",
  Enfileirado: "Queued",
  Convertendo: "Converting",
  "Não aplicável": "Not applicable",
  Temporário: "Temporary",
  Aguardando: "Waiting",
  Validando: "Validating",
  Exportando: "Exporting",
  Original: "Source",
  Aplicação: "Application",
  "Banco de dados": "Database",
  "Diretório de upload": "Upload directory",
  "Partner configurado": "Partner configured",
  "Endpoint de upload": "Upload endpoint",
  "API acessível (system.ping)": "API reachable (system.ping)",
  "Autenticação (KS admin)": "Authentication (admin KS)",
  "Em execução.": "Running.",
  "Conexão ativa.": "Connected.",
  "Sem conexão.": "Not connected.",
  "Gravável.": "Writable.",
  "Sem permissão de escrita.": "Not writable.",
  "Endpoint dedicado configurado.": "Dedicated endpoint configured.",
  "Usando service_url para uploads.": "Using service_url for uploads.",
  "Respondeu.": "Responded.",
  "Sem resposta.": "No response.",
  "KS admin obtida.": "Admin KS obtained.",
  "Falha ao obter a KS.": "Unable to obtain KS.",
  "Chamada bem-sucedida.": "Call succeeded.",
  "Falhou.": "Failed.",

  Painel: "Dashboard",
  Mídia: "Media",
  Usuários: "Users",
  "Saúde do sistema": "System health",
  Sair: "Sign out",
  Biblioteca: "Library",
  Upload: "Upload",
  Ajuda: "Help",
  Entrar: "Sign in",
  "E-mail": "Email",
  Senha: "Password",
  "Lembrar-me": "Remember me",
  Nome: "Name",
  Descrição: "Description",
  Status: "Status",
  Duração: "Duration",
  "Criado em": "Created",
  Buscar: "Search",
  Anterior: "Previous",
  Próxima: "Next",
  Enviar: "Upload",
  Salvar: "Save",
  Excluir: "Delete",
  Cancelar: "Cancel",
  "Arquivo MP4": "MP4 file",
  "Enviando ao console": "Sending to console",
  "Enviando ao Kaltura": "Sending to Kaltura",
  Processando: "Processing",
  Pronto: "Ready",
  Erro: "Error",
  Total: "Total",
  Recentes: "Recent entries",
  Resolução: "Resolution",
  Tamanho: "Size",
  Formato: "Format",
  Tipo: "Type",
  Papel: "Role",
  "Adicionar usuário": "Add user",
  "Redefinir senha": "Reset password",
  Atualizar: "Refresh",
  "Nenhum resultado": "No results",
  "Carregando…": "Loading…",
  "Operação concluída": "Operation completed",
  "Confirmar exclusão?": "Confirm deletion?",
  Administrador: "Administrator",
  Visualizador: "Viewer",
  "Falha ao carregar flavors": "Unable to load flavors",
  "Vídeo indisponível": "Video unavailable",
  "Selecione um arquivo": "Select a file",
  "Aguardando processamento no Kaltura": "Waiting for Kaltura processing",
  "Consulta automática encerrada. Atualize para consultar novamente.":
    "Automatic polling stopped. Refresh to check again.",
  "Gerencie os vídeos do seu partner Kaltura.":
    "Manage videos for your Kaltura partner.",
  "Use seu e-mail e senha locais. Contate o administrador para obter acesso.":
    "Use your local email and password. Contact your administrator for access.",
  "Pesquise por nome. Apenas administradores podem modificar os vídeos.":
    "Search by name. Only administrators can modify videos.",
  "Envie um MP4. Aguarde as etapas de envio e processamento.":
    "Upload an MP4. Wait for transfer and processing.",
  "A reprodução passa pelo console. O status é atualizado a cada 5 segundos.":
    "Playback goes through the console. Status refreshes every 5 seconds.",
  "Gerencie contas locais. O último administrador não pode ser removido.":
    "Manage local accounts. The last administrator cannot be removed.",
  "Os testes são independentes e não exibem segredos.":
    "Checks are independent and never display secrets.",
};
export function t(text: string) {
  if (locale.value !== "en") return text;
  if (text.startsWith("Banco de dados ("))
    return text.replace("Banco de dados", "Database");
  return en[text] ?? text;
}
export function changeLocale(value: string) {
  locale.value = value;
  localStorage.setItem("locale", value);
  document.documentElement.lang = value;
}
