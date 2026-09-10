# SPEC — Validação Walk-Forward

**Versão:** 0.1  
**ADR relacionadas:** 0002

## 1. Definições

| Termo | Descrição |
|-------|-----------|
| `origin_date` | Última data do histórico usado para treinar e gerar previsão |
| `horizon` (h) | Quantos passos à frente prever a partir da origem |
| `test_period` | Intervalo onde origens são avaliadas |
| `train_window` | Mínimo de observações antes da primeira origem |

## 2. Parâmetros globais (pendente ADR-0005)

```yaml
horizon: null          # ex.: 7
train_min_obs: null    # ex.: 365
first_origin: null     # timestamp
last_origin: null      # timestamp
origin_step: 1         # frequência entre origens
```

> Todos os modelos e bases usam os **mesmos** valores.

## 3. Algoritmo

```
Para cada origin_date em origens:
    train = dados[:origin_date]
    ajustar hiperparâmetros FIXOS (pré-selecionados)
    y_pred = modelo.predict(horizon=h)
    y_true = dados[origin_date+1 : origin_date+h]
    registrar previsão, resíduo, tempo
    avançar origin_date
```

## 4. Separação tuning vs teste

| Fase | Uso dos dados | Hiperparâmetros |
|------|---------------|-----------------|
| Tuning | Validação interna antes do teste | Busca no espaço definido |
| Avaliação final | Período de teste walk-forward | **Fixos** |

## 5. Saídas

Salvar em `data/base_XX/`:

| Artefato | Arquivo |
|----------|---------|
| Previsões OOS | `predictions_{modelo}_{base_id}.csv` |
| Colunas mínimas | `origin_date`, `forecast_date`, `y_true`, `y_pred`, `horizon_step` |
| Modelo treinado | `artifacts/base_XX/{modelo}.pkl` |

## 6. Validação de conformidade

- [ ] Mesmo número de previsões OOS para todos os modelos na mesma base
- [ ] Nenhum modelo acessa dados após `origin_date` no treino/features
