# Segurança e privacidade

O TokenLens 0.1 é experimental. O lab escuta apenas em 127.0.0.1 e não deve ser
exposto por túnel, proxy, rede pública ou hospedagem. Não é um serviço multiusuário.
Processos da mesma conta podem ler seu banco; o armazenamento não é criptografado.

Somente eventos de contrato fechado são persistidos. Não são permitidos prompts,
respostas, código, nomes de projetos, caminhos, identificadores nativos ou segredos.
Os bridges processam saída nativa transitoriamente em memória para selecionar
metadados. Isso não garante zero contato com conteúdo em memória nem altera as
políticas de transmissão/armazenamento dos provedores.

Use dados sintéticos para testes e relatos. Nunca anexe bancos, transcrições,
configurações, capturas de sessões reais ou credenciais a issues. Para reportar
vulnerabilidades, use a opção privada de Security Advisories no repositório, quando
habilitada. Se indisponível, solicite um canal privado sem divulgar detalhes.

Antes de cada release, execute a suíte sintética e `scripts/release.py`. O scanner
é uma defesa adicional com padrões conhecidos; não prova ausência de todo segredo.
Revise o manifesto gerado. Diretórios locais são excluídos por allowlist.

Não use `git add -f` para incluir `.local`, `.venv`, bancos ou logs.
