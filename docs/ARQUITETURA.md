# Decisões v0.1 — 2026-10-05

O JSON original foi preservado. Este documento registra os refinamentos acordados
na conversa e as limitações descobertas durante a implementação.

1. Core distribuível independente; dashboard e bridges locais opcionais.
2. Dashboard antecipado para apoiar validação; somente metadados também no lab.
3. Dados reais e sintéticos separados em consultas. Nenhum dado real entra no pacote.
4. Categorias e complexidade manuais ou desconhecidas; sem classificação de prompts.
5. Sugestões determinísticas, sem roteamento, sem alegações de economia comprovada.
6. Nenhum identificador original de projeto, conta ou sessão é armazenado. Nesta
   versão não há agrupamento por projeto/sessão; event_id é UUID gerado localmente.
7. Campos extras são rejeitados recursivamente. Nomes de modelos são allowlist
   explícita pública; modelos desconhecidos viram null, não texto livre.
8. Tokens de entrada incluem cache; total = entrada + saída. Cache e raciocínio
   são subconjuntos, não parcelas extras. Ausente é null, nunca zero presumido.
9. Snapshot de contexto não é uma execução, não é somado a consumo.
10. Não há equivalência assumida entre modelos, provedores ou níveis de raciocínio.

## Fronteira de privacidade

Banco, API do dashboard, erros do TokenLens e pacotes aceitam apenas o contrato.
Nenhum payload bruto é persistido, retransmitido ou exibido pelo TokenLens.
O dashboard não aceita logs nativos nem texto livre; toda saída DOM usa textContent.

Há uma distinção essencial: CLIs nativas produzem payloads mistos. O bridge local
precisa recebê-los transitoriamente em memória para extrair contadores. O bridge
descarta mensagens, diretórios, IDs e conteúdo imediatamente, sem registrar esses
valores. Isso NÃO permite prometer que dados sensíveis nunca passam pela memória
de um processo de integração. Se a regra exigir zero contato até em memória,
as conexões nativas devem permanecer desligadas e somente eventos previamente
normalizados podem entrar. Nunca usamos conteúdo para classificar tarefas.

As CLIs têm suas próprias políticas de armazenamento e transmissão ao provedor;
TokenLens não muda essas políticas. `--ephemeral` / `--no-session-persistence`
limitam persistência nas execuções de medição. Não afirmamos apagar dados mantidos
pelo provedor ou pelo sistema operacional. Metadados também podem revelar padrões
de trabalho; “sem conteúdo sensível” não é garantia matemática de anonimato.

## Integrações e evidência

| Provedor | Fonte usada | Limite |
| --- | --- | --- |
| Codex | `exec --json`, evento `turn.completed` | Não monitora sessões interativas normais; modelo pode faltar |
| Claude Code | resultado stream-json | Modo de medição, sem ferramentas; saída da IA descartada |
| Claude Code | status line | Contexto atual, não consumo acumulado |
| Antigravity | nenhum conector nativo ativado | Capacidade pendente, sem falsa equivalência |

Não ativamos OpenTelemetry amplo: pode conter identificadores e trechos de saída.
Não lemos histórico de conversas, configurações com segredos ou bancos internos.

## Fontes oficiais consultadas

- [Codex não interativo](https://developers.openai.com/codex/noninteractive/): eventos JSON e uso por conclusão.
- [Codex telemetria](https://developers.openai.com/codex/config-advanced/): exportação ampla pode conter metadados identificadores e conteúdo de ferramentas.
- [Claude status line](https://code.claude.com/docs/en/statusline): campos de contexto e comando local.
- [Claude monitoramento](https://code.claude.com/docs/en/monitoring-usage): semântica de cache e limites dos atributos.
- [Antigravity CLI](https://www.antigravity.google/docs/cli/reference/): comandos documentados; não assumimos uma exportação automática segura.

## Próximas validações

- Verificar telemetria real e modelo efetivo em cada versão instalada, sem inventar campos.
- Evoluir conexão observadora do Codex interativo quando existir fonte seletiva segura.
- Validar coleta do Antigravity em ambiente em que esteja instalado.
- Definir agrupamento anônimo e retenção antes de acumular grandes históricos.
- Calibrar recomendações somente após obter medidas de resultado/qualidade.
