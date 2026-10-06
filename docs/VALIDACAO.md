# Validação de distribuição

Esta edição usa somente dados sintéticos. Não contém resultados individuais de uso.

Execute `python scripts/test_synthetic.py`, `node scripts/test_chart.cjs`,
`python -m build --no-isolation --outdir dist/core core`, `python scripts/release.py` e
`python scripts/check_wheel.py`.

A suíte impede execução de CLIs reais e conexões externas no processo de testes.
Subprocessos são restritos ao Python e usam payloads fictícios.
O workflow inclui Windows/Linux e Python 3.11–3.13; resultados remotos só são
confirmados depois de o GitHub executar o workflow.

Integrações ao vivo, login, qualidade de modelos e cobertura de Antigravity não são
validados por esta suíte. O relatório anterior da máquina não integra a distribuição.

Validação local desta edição: 35 testes Python aprovados, agregação do gráfico,
interações do dropdown e fluxo do dashboard aprovados em DOM sintético.
Wheel independente instalado por extração em diretório temporário e validado.
Verificação visual final no navegador não foi concluída por indisponibilidade
da ferramenta de automação; os testes DOM não substituem uma revisão visual.
