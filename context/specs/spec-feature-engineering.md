# SPEC — Feature Engineering

**Versão:** 0.1  
**ADR relacionadas:** 0003

## 1. Princípios

- Features calculadas **apenas** com informação disponível na `origin_date` do walk-forward.
- **Mesmo conjunto** para Random Forest e modelo de especialização (quando compatível).
- SARIMAX usa variáveis externas conforme disponibilidade (não necessariamente o mesmo vetor tabular).

## 2. Features mínimas

| Categoria | Exemplos | Parâmetros |
|-----------|----------|------------|
| Lags do alvo | `target_lag_1`, `target_lag_7` | Lista de lags por base |
| Lags de externas | `ext_temp_lag_1` | Só se `availability = lag_only` |
| Janelas móveis | média, desvio padrão | Janelas: [DEFINIR] |
| Calendário | dia da semana, mês, feriado | `known_ahead` |
| Encoding cíclico | sin/cos para hora, dia do ano | Período sazonal m |

## 3. Tratamento de NaN

- Lags/janelas geram NaN no início da série → estratégia documentada:
  - [ ] Drop de linhas iniciais no treino
  - [ ] Forward-fill limitado (justificar)
  - [ ] Imputação (evitar se introduzir vazamento)

## 4. Anti-leakage (checklist)

- [ ] Nenhuma coluna usa valor com timestamp > origin_date
- [ ] Scaler fit apenas no treino do fold atual
- [ ] Variáveis `forecast_at_origin` identificadas no dicionário
- [ ] Features futuras do alvo **proibidas**


## 5. Saída

- Features documentadas no notebook (`notebooks/base_XX.ipynb`)
- Matriz persistida em `data/base_XX/features_{base_id}.parquet` (quando aplicável)
- Célula markdown listando features finais e parâmetros (lags, janelas)
