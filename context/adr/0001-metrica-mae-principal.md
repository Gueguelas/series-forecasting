# ADR-0001: MAE como métrica principal de comparação

**Status:** Aceita  
**Data:** 2026-09-10  
**Fonte:** `docs/instrucoes.pdf` seção 6

## Contexto

O enunciado define o Mean Absolute Error (MAE) como métrica principal para comparar os quatro modelos em cada base. As bases podem ter escalas diferentes.

## Decisão

1. Usar **MAE** calculado sobre previsões **fora da amostra** do walk-forward.
2. Apresentar MAE **por base** (5 valores por modelo).
3. Ranquear modelos **dentro de cada base** (menor MAE = melhor).
4. Consolidar desempenho global por **vitórias** e **posição média** — não por média ou soma de MAE entre bases.

## Alternativas consideradas

| Alternativa | Motivo da rejeição |
|-------------|-------------------|
| RMSE / MAPE | Não são métricas do enunciado |
| Média de MAE entre bases | Escalas diferentes invalidam agregação direta |

## Consequências

- Implementação nos notebooks (`notebooks/base_XX.ipynb`) e consolidação em `relatorio.ipynb`
- Tabela consolidada de MAE na seção 8 do relatório
- Relatório: seção 8 conforme PRD
