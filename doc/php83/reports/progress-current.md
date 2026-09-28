# PHP 8.3 — status atual e tarefas restantes

Atualizado: 2026-09-28T18:59:43.713726+00:00

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
| Coletor baseline R2 |28 testes locais; observação nativa exit0|Marco histórico parcial; substituído pelas observações V2 abaixo, não é freeze aprovado|

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

- V2: coleta real exit0, fixture tipado com seleção explícita media.get(-1),
  versão de dados0 separada da versão2 do asset. Três janelas de privacidade
  completas sem correspondências. Fonte/testes revistos independentemente.
- Perfil14: cinco SELECT limitados, somente leitura, exit0/stderr0; pertence ao
  parceiro102, status2/tipo1, não excluído, oito flavors configurados. Isso não
  resolve a autorização de consulta do perfil pela API.
- Apache: teste real exit0/stderr0, PHP7.4.33/apache2handler e53 módulos,
  /etc/php/7.4/apache2/php.ini; nonce confirmado, arquivo próprio removido,
  unidade inativa e identidade da VM preservada. Revisão independente aprovada.
- Testes auxiliares:39 do coletor V2,8 do observador SQL e13 do wrapper web,
  incluindo limpeza real de fixture local sob SIGTERM. Não são tarefas completas.
- Ensaio nativo corrigido R2:100/100 chamadas válidas,34 sessões/33 listagens/
  33 consultas;72 marcadores em três janelas completas sem correspondência.
  Exit0, unidade inativa e revisão independente aprovada. Falha UNDRAINED_TAIL
  da rodada anterior preservada; a correção aguarda estabilidade limitada sem
  avançar o início da janela nem omitir logs.
- HTTPS isolado instalado em192.168.56.74:8443: TLS1.3, CA privada/IP SAN
  validada, CA incorreta rejeitada; HTTP80 e móduloPHP7 preservados. Teste real
  HTTP após o restart confirmou PHP7.4.33/apache2handler e removeu o próprio
  arquivo de prova. Nenhum segredo/chave exportado. R1 bloqueado por metadados
  permanece preservado; R2 usa diretório de logs próprio sem chmod em /var/log.
- HTTPS autenticado:100/100 chamadas válidas, CA fixada,72 marcadores verificados
  sem correspondência em janelas completas, incluindo os dois novos logs.
  Exit0/unidade inativa; revisão independente aprovada. É ensaio funcional,
  não benchmark ou aceite completo da tarefa.
- Metadados reais da mídia curta:7 assets,4 READY (original e3 versões) e3
  NOT_APPLICABLE, conforme enum nativo. Consulta viaHTTPS exit0, janelas de
  privacidade completas e revisão independente aprovada. Não inferimos motivo
  dos3 itens nem aceite de reprodução a partir apenas do status.
- Próximo:download/Range da mídia existente, HLS, mídia longa/UI e medições
  formais. Tarefa1.2 ainda aberta.

R1/R2 e seus resultados parciais/falhos permanecem preservados. Tarefa1.2 aberta;
nenhuma alteração em produção. Fonte do box: novo download oficial de651.326.766
bytes, SHA14ae82e423c270d1c03907faf90691b0fbd673b16bfc369a949808e4e6991b82,
com quatro arquivos correspondentes ao cache; não prova retrospectiva do
provisionamento ou identidade do disco atual.
