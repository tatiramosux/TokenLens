# Configuração e uso local

## 1. Obter o código

Clone o repositório público:

```powershell
git clone https://github.com/tatiramosux/TokenLens.git
cd TokenLens
```

Requisitos: Python 3.11 ou superior; CLIs somente se quiser conectar dados reais.
O modo demonstrativo não exige conta, chave, assinatura ou CLI.

## 2. Instalar o ambiente isolado

No PowerShell, dentro da pasta clonada:

```powershell
./scripts/Setup.ps1
```

Se Python não estiver no PATH, passe o executável instalado:

```powershell
./scripts/Setup.ps1 -Python 'CAMINHO_DO_PYTHON/python.exe'
```

O script instala dependências em `.venv`; não altera Python global. Precisa de
internet para baixar dependências. Depois disso, core, lab e regras funcionam
offline. As CLIs continuam precisando do acesso exigido por seus provedores.

Em Linux/macOS: `python3 -m venv .venv`, depois `.venv/bin/python -m pip install -r requirements-dev.txt`
e `.venv/bin/python -m pip install --no-build-isolation --no-deps -e ./core`.
Use `.venv/bin/python` nos comandos abaixo. Launchers PowerShell são para Windows.

## 3. Abrir o dashboard

```powershell
./scripts/Start-Lab.ps1
```

Abra http://127.0.0.1:8765. Mantenha o terminal do servidor aberto. Ctrl+C encerra.
O serviço escuta exclusivamente no loopback IPv4, rejeita origens externas e
nomes de host diferentes de `127.0.0.1`. Não publique nem faça proxy desse serviço.
Uma conta local capaz de ler os arquivos ainda pode ler as métricas; não há
criptografia de banco nem proteção contra processos maliciosos na mesma conta.

Selecione **Demonstração** para explorar. Os exemplos incluem Antigravity, mas
não representam uma integração automática com ele. Filtros também afetam sugestões.

## 4. Conectar Codex e Claude em execuções de medição

As CLIs devem estar instaladas, no PATH e autenticadas pelo fluxo oficial de cada
uma. TokenLens não solicita, copia ou inspeciona credenciais.

Primeiro, execute um teste curto (pode consumir tokens da sua assinatura/conta):

```powershell
./.venv/Scripts/python.exe -m bridges.measure codex --smoke --timeout 60
./.venv/Scripts/python.exe -m bridges.measure claude_code --smoke --timeout 60
```

O teste envia apenas uma instrução sintética pedindo `OK`, sem solicitar leitura
de arquivos. O bridge descarta respostas, erros brutos e identificadores.
Procure `Medições salvas: 1` ou mais e atualize **Uso real** no dashboard.
Detectar o executável, iniciar o processo ou validar exemplos NÃO prova essa coleta.
Se não houver métricas, confira login e conectividade diretamente na CLI.

Para medir uma tarefa digitada no terminal sem registrá-la no histórico do shell:

```powershell
./.venv/Scripts/python.exe -m bridges.measure codex --category planning --complexity medium
```

Digite a instrução no stdin; no Windows finalize com Ctrl+Z e Enter.
Esta é uma ferramenta de **medição não interativa**: a resposta da IA é descartada.
Não substitui o terminal normal para trabalho interativo. Codex usa sandbox
somente leitura; Claude nesta modalidade é iniciado sem ferramentas.
O tempo padrão máximo é 120 segundos, configurável com `--timeout`.

O modelo efetivo pode não estar presente na saída da CLI. Nesse caso aparece
“Modelo não informado”, mesmo se foi solicitado um modelo específico.

## 5. Claude interativo: observar o contexto

No PowerShell, estando no projeto em que deseja trabalhar, execute o launcher por
caminho absoluto ou relativo:

```powershell
./scripts/Start-Claude.ps1
```

O launcher inicia Claude com uma status line TokenLens válida somente nessa
invocação. Não altera `~/.claude/settings.json`, credenciais ou configurações globais.
Uma status line existente fica substituída apenas nessa execução; ao iniciar
`claude` normalmente, sua configuração original volta a valer.

O bridge recebe o JSON nativo em memória e seleciona apenas modelo permitido e
contadores de contexto. Ignora diretórios, nomes e identificadores da sessão;
não abre o arquivo de transcrição. Esses dados aparecem como **context snapshots**,
separados de consumo: janela de contexto NÃO é consumo acumulado.
Esta conexão precisa ser confirmada em uma sessão interativa pelo usuário.

## 6. Antigravity

O adaptador existe e informa ausência de suporte. A coleta automática não foi
ativada: não há fonte segura verificada neste ambiente e o executável não foi
encontrado no PATH. Não acessamos bancos internos, tokens ou sessões para contornar
essa limitação. As métricas demonstrativas não mudam esse status.

## 7. Categorias e sugestões

Selecione categoria/complexidade e clique **Salvar**. Sem indicação manual,
esses campos ficam desconhecidos. Sugestões são regras transparentes e locais,
sem consumo adicional de IA. Não afirmam que um modelo está superdimensionado
sem evidência de qualidade. Quotas e custos não são estimados de tokens.

## 8. Distribuir core e lab separadamente

```powershell
./.venv/Scripts/python.exe -m build --no-isolation --outdir dist/core core
```

Compartilhe somente os arquivos em `dist/core` para distribuir o core. Dashboard,
bridges, dados e configurações locais não fazem parte do wheel ou do sdist.
Para clonar o lab, compartilhe o repositório-fonte com `.gitignore` aplicado.
O arquivo `requirements-dev.txt` fixa as versões usadas nesta primeira construção.

## 9. Parar e remover

Encerre o servidor com Ctrl+C e saia das CLIs iniciadas pelos launchers. Nenhum
serviço foi instalado no Windows e nenhum processo inicia automaticamente no login.
Para apagar métricas, com o servidor parado, remova apenas `.local/telemetry.sqlite3`
dentro do clone. Para remover o ambiente, remova `.venv` desse clone. Isso não remove
as CLIs nem seus históricos. Não apague pastas pessoais dos provedores.
