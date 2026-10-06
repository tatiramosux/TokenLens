# TokenLens

Laboratório local de observabilidade para CLIs de IA. Python 3.11+, SQLite e um
dashboard sem serviços externos, fontes remotas, analytics ou chamadas a modelos.

## Começar no Windows

```powershell
./scripts/Setup.ps1
./scripts/Start-Lab.ps1
```

Abra http://127.0.0.1:8765. O modo inicial é **Uso real**, possivelmente vazio.
**Demonstração** usa 36 medições fictícias e não comprova conexões.

Leia o [guia de configuração e uso](docs/CONFIGURACAO.md) e as
[decisões e limites de privacidade](docs/ARQUITETURA.md).

## Separação

- `core/`: pacote Python agnóstico, distribuível sozinho.
- `lab/`: dashboard opcional, fora da distribuição do core.
- `bridges/`: integração local, fora da distribuição do core.
- `scripts/`: instalação e launchers reversíveis.
- `.local/`: dados da máquina, ignorados pelo Git e excluídos dos pacotes.
- `tokenlens_architecture_handoff_v0.1.json`: especificação original preservada.

As pastas são irmãs dentro deste workspace; não foi necessário escrever fora dele.
O lab pode ser compartilhado como código, sem compartilhar os dados de uso.
Repositório: https://github.com/tatiramosux/TokenLens.

## Verificação

```powershell
./.venv/Scripts/python.exe -m unittest discover -s core/tests -v
./.venv/Scripts/python.exe -m build --no-isolation --outdir dist/core core
```

O dashboard permite filtrar período, provedor, modelo e categoria, classificar
manualmente tarefas e ler sugestões por regras locais. Não infere qualidade a
partir de tokens, não lê prompts para classificar e não roteia modelos.

## Testar sem dados reais

```powershell
./.venv/Scripts/python.exe scripts/test_synthetic.py
node scripts/test_chart.cjs
./.venv/Scripts/python.exe scripts/simulate.py
./.venv/Scripts/python.exe -m lab.server --db .local/synthetic.sqlite3
```

Selecione Demonstração. Não execute `bridges.measure --smoke`: apesar do prompt
sintético, esse comando usa uma CLI autenticada e pode consumir tokens reais.
O gráfico agrupa consumo por data, CLI e modelo. A lista de opções e o tema
são locais, sem bibliotecas de interface ou fontes externas.

Licença: [MIT](LICENSE). Veja [contribuição](CONTRIBUTING.md) e [segurança](SECURITY.md).

## Distribuição

```powershell
./.venv/Scripts/python.exe -m build --no-isolation --outdir dist/core core
./.venv/Scripts/python.exe scripts/release.py
./.venv/Scripts/python.exe scripts/check_wheel.py
```

`dist/core` contém apenas o core; `dist/tokenlens-lab-source.zip` contém o lab
e seu código de apoio por allowlist. O manifesto e os hashes ficam em `dist`.
Os artefatos não incluem bancos, capturas locais, ambientes ou credenciais.

Para testes dos dropdowns: `npx pnpm@11.19.0 install --frozen-lockfile --ignore-scripts`
e `node scripts/test_dropdown.cjs` (Node.js necessário apenas para testes de UI).
