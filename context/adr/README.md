# ADRs — Architecture / Analytics Decision Records

Registro de decisões metodológicas e técnicas do projeto.

## Status

| ADR | Título | Status |
|-----|--------|--------|
| [0000](0000-template.md) | Template | — |
| [0001](0001-metrica-mae-principal.md) | MAE como métrica principal | Aceita |
| [0002](0002-validacao-walk-forward.md) | Validação walk-forward | Aceita |
| [0003](0003-prevencao-vazamento-dados.md) | Prevenção de vazamento temporal | Aceita |
| [0004](0004-estrutura-repositorio.md) | Notebooks + `data/` local | Aceita |
| [0005](0005-persistencia-artifacts-dados.md) | Pickles em `artifacts/`, nomenclatura em `data/` | Aceita |

## Convenções

- Numeração sequencial: `0001`, `0002`, …
- Nome do arquivo: `NNNN-titulo-curto.md`
- Status: `Proposta` → `Aceita` → `Substituída` / `Obsoleta`
- Decisão aceita **não é editada**; mudança exige nova ADR que referencia a anterior

## Quando criar

- Escolha de horizonte, origens ou período sazonal
- Tratamento de variável externa ambígua
- Mudança de modelo, base ou biblioteca
- Qualquer alteração que o enunciado exige "aprovação prévia"
