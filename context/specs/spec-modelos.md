# SPEC — Modelos

**Versão:** 0.2  
**PRD:** seções 3, 5.5, 8, 9  
**ADR:** 0005

## 1. Inventário (20 combinações)

5 bases × 4 modelos:

| Modelo | Externas | Papel |
|--------|----------|-------|
| SARIMAX | Sim | Modelo estatístico com exógenas |
| Holt-Winters | Não | Referência univariada |
| Random Forest | Sim | ML com importância nativa |
| Elastic Net | Sim | Modelo de especialização (Grupo 3) |

\* Conforme compatibilidade do algoritmo.

## 2. Hiperparâmetros mínimos a investigar

### SARIMAX
- Ordens (p, d, q), sazonais (P, D, Q), período m
- Critério AIC/BIC
- Seleção de variáveis externas

### Holt-Winters
- Tendência, sazonalidade, tendência amortecida
- Período sazonal, parâmetros de suavização

### Random Forest
- `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`, `max_features`

### Elastic Net (Grupo 3 — especialização)

- Hiperparâmetros principais: `alpha`, `l1_ratio`
- Requer padronização das features antes do ajuste
- Interpretação: coeficientes após padronização
- Slug de arquivo: `elastic_net` (`predictions_elastic_net_{base_id}.csv`, `elastic_net.pkl`)

## 3. Otimização

Documentar por modelo × base:

| Campo | Conteúdo |
|-------|----------|
| Espaço de busca | Grid / random / Bayesian — ranges |
| Procedimento | Como evita o conjunto de teste final |
| Valores finais | Hiperparâmetros escolhidos |
| Justificativa | Por que a configuração final |

## 4. Interpretação / feature importance

| Modelo | Método |
|--------|--------|
| SARIMAX | Coeficientes, sinal, magnitude, significância |
| Holt-Winters | Nível, tendência, sazonalidade (sem FI) |
| Random Forest | Importância nativa e/ou Permutation |
| XGBoost | Gain, Permutation ou SHAP |
| SVR | Permutation (ou equivalente) |
| Elastic Net | Coeficientes padronizados |
| MLP | Permutation (ou equivalente) |
| PLS | Coeficientes, Permutation ou VIP |

## 5. Interface por modelo

```python
class Forecaster(Protocol):
    def fit(self, train: pd.DataFrame, exog: pd.DataFrame | None) -> None: ...
    def predict(self, horizon: int, exog_future: pd.DataFrame | None) -> pd.Series: ...
    def get_params(self) -> dict: ...
```

## 6. Persistência

### Modelos treinados → `artifacts/`

```
artifacts/{base_id}/{modelo}.pkl
artifacts/{base_id}/{modelo}_meta.json
```

Exemplo: `artifacts/base_01/random_forest.pkl`

Ver [`artifacts/README.md`](../../artifacts/README.md).

### Hiperparâmetros → `data/`

```
data/{base_id}/hyperparams_{modelo}_{base_id}.json
```

## 7. Registro por execução

- Parâmetros finais (em `_meta.json` e notebook)
- Tempo de execução
- Versão das bibliotecas
- Seed
