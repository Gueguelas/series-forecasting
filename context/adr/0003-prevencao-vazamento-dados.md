# ADR-0003: Prevenção de vazamento temporal (data leakage)

**Status:** Aceita  
**Data:** 2026-09-10  
**Fonte:** `docs/instrucoes.pdf` seções 4.1, 5.3 e 5.6

## Contexto

Variáveis externas podem não estar disponíveis na data real da previsão. Usar valores futuros observados como feature invalida a comparação e reproduz resultados irreais.

## Decisão

Para cada variável externa, documentar na spec de dados:

| Disponibilidade | Tratamento |
|-----------------|------------|
| Conhecida antecipadamente (calendário, feriados) | Usar valor da data prevista |
| Planejada antecipadamente (preço, promoção) | Usar valor planejado se disponível na origem |
| Observada só no futuro (temperatura real) | **Proibido** — usar lag, previsão meteorológica na origem, ou excluir |
| Previsão disponível na origem | Usar e **identificar** como previsão |
| Indisponível no futuro | Lag, proxy ou exclusão justificada |

Regras adicionais:

1. Lags e janelas móveis usam apenas passado relativo à data de origem.
2. Normalização/escalonamento: fit apenas no treino de cada fold walk-forward.
3. Otimização de hiperparâmetros não pode usar o conjunto de teste final.

## Consequências

- Coluna `availability` no dicionário de variáveis (`spec-dados.md`)
- Checklist de revisão em cada PR humano e em HANDOFF
- Testes automatizados recomendados para features críticas
