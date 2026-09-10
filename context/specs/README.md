# SPECS — Especificações técnicas

Detalhamento implementável derivado do [`PRD.md`](../PRD.md) e [`SDD.md`](../SDD.md).

| Spec | Domínio |
|------|---------|
| [spec-dados.md](spec-dados.md) | Bases, dicionário, limpeza, EDA |
| [spec-feature-engineering.md](spec-feature-engineering.md) | Features, lags, calendário |
| [spec-validacao.md](spec-validacao.md) | Walk-forward, origens, horizonte |
| [spec-modelos.md](spec-modelos.md) | 4 modelos e hiperparâmetros |
| [spec-avaliacao.md](spec-avaliacao.md) | MAE, resíduos, Ljung-Box, importance |
| [spec-relatorio.md](spec-relatorio.md) | HTML paginado, PDF, entrega |

Cada spec deve ser atualizada quando uma ADR alterar o comportamento correspondente.

**Entregas:** notebooks em `notebooks/` (um por dataset) · dados fornecidos ao grupo em `data/` (gitignored).
