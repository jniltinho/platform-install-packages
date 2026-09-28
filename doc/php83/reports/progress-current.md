# PHP 8.3 — status atual e tarefas restantes

Atualizado: 2026-09-28T17:58:42.816852+00:00

**5 concluídas / 46 abertas / 51 tarefas.** Os 24 requisitos originais e 27 casos detalhados se sobrepõem; não são 51 funcionalidades independentes. Sem percentual ou previsão de conclusão inferidos de testes.

## Contagem por área

| Área | Concluídas | Abertas |
|---|---:|---:|
| 1. Baseline and feasibility gate | 2 | 5 |
| 2. Compatibility patches and packaging | 0 | 6 |
| 3. Isolated runtime acceptance | 0 | 6 |
| 4. Upgrade, recovery and release gate | 0 | 5 |
| 5. Approved detailed test cases | 3 | 24 |

## Novo marco concluído

1.1: inventário reproduzível aprovado independentemente. 15.175 arquivos extraídos,
13.454 arquivos PHP dos pacotes relacionados, 4.999 arquivos vendor cobertos;
revisões/licenças desconhecidas explicitamente preservadas. Não significa aprovação
legal ou runtime. Registro: ../task-1.1-inventory-acceptance.md. Commit63c029d5
publicado na branch proposal/migrate-kaltura-php83.

## Trabalho atual: 1.2

- Laboratório .74 confirmado read-only: PHP7.4.33,4CPU/8GiB. Contexto publicado em
  f3947d90. Não é atestação completa ou baseline aprovado.
- Novo coletor do fixture existente e contrato em implementação/revisão independente.
  28 testes locais do coletor/runner e36 testes existentes do protocolo passaram.
  Coleta nativa R2 exit0, unidade encerrada e três janelas finitas de privacidade
  completas com zero correspondências; sem upload ou mudança de perfil.
- Faltam completar protocolo/ambiente, HTTPS/HLS/mídia longa/worker, UI e as
  repetições/medições exigidas. Overlay de privacidade V4 permanece distinguido
  do baseline publicado intacto.

## Estatísticas de validação deste avanço

| Escopo | Resultado executado | Limite |
|---|---|---|
| Inventário |17 testes; reprodução independente idêntica|Não é runtime|
| Censo lexical corrigido |8 testes; reprodução independente idêntica|Não resolve aplicabilidade legal|
| MaxMind |35 arquivos idênticos;5 negativos rejeitados|Não prova versão original única|
| Contexto .74 |4 testes root/Codex/Claude; coleta real exit0|Não é freeze completo|
| Coletor baseline R2 |28 testes locais; observação nativa exit0|Versão concreta/perfil ainda não resolvidos; não é freeze aprovado|

Contagens acima se sobrepõem; não são somadas como tarefas concluídas. Tentativas
Claude/OpenCode incompletas e Cursor sem autenticação não são PASS.

## Preservação e comunicação

Instalação incremental .83 dos17 pacotes foi concluída no marco anterior; nginx
permanece parado e workers retidos conforme último recibo, sem nova consulta aqui.
Produção .20, releases e gates finais inalterados. As outras45 tarefas abertas,
além da1.2 atual, estão enumeradas em tasks-current.csv.

E-mail da1.1: tentativa SMTP expirou; envio NÃO confirmado. Recibo específico
preservado, sem reenvio automático. O relatório antigo foi arquivado com timestamp;
seus bloqueadores históricos não representam este status atual.

## Resultado nativo mais recente

R1 falhou na captura e foi preservado (c951138b); R2 corrigiu a captura de
observações incompletas e terminou exit0. `media.get(-1)` e `media.get(0)`
coincidiram em projeção tipada. Fixture continua nulo e perfil14 ainda não
classificado. Revisão de fonte encontrou duas hipóteses específicas do helper:
exigia versão positiva que a API não exige e esperava nome incorreto da classe
de perfil. Próxima correção será versionada/revisada, sem alterar o protocolo
antigo nem inventar versão a partir do asset2. Tarefa1.2 permanece aberta.

Fonte do box: novo download oficial de651.326.766 bytes, SHA
14ae82e423c270d1c03907faf90691b0fbd673b16bfc369a949808e4e6991b82;
os quatro arquivos correspondem ao cache atual. Não é prova retrospectiva de
provisionamento nem identidade do disco da VM em execução.
