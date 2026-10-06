# Contribuir

1. Crie o ambiente com `scripts/Setup.ps1` ou siga `docs/CONFIGURACAO.md`.
2. Execute `python scripts/test_synthetic.py` com o Python do ambiente virtual.
3. Execute `python -m build --no-isolation --outdir dist/core core` e `python scripts/release.py`.
4. Abra um PR explicando comportamento, limite e teste sintético reproduzível.

Não use contas ou dados reais na suíte. Não inclua segredos nem payloads reais,
mesmo em testes de privacidade. As fixtures de rejeição usam canários fictícios.
Não adicione coleta de conteúdo, classificação por prompts ou roteamento automático.

O contrato rejeita campos desconhecidos. Para um provedor novo, implemente o
protocolo `Adapter`, normalize para `provider=other` e `source=manual` enquanto
não houver vocabulário público aprovado. Campos indisponíveis ficam null.
Mudanças incompatíveis exigem versão de schema e plano de migração.

Core e lab são separados por empacotamento: execute os testes de independência
do wheel, não copie o dashboard para dentro de `core/src`.

Licença: MIT. Ao contribuir, você concorda em disponibilizar sua contribuição sob essa licença.
