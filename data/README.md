# Dados — organização local


1. **Arquivos fornecidos ao grupo** (raw, como recebidos)
2. **Qualquer dado derivado** gerado pela análise (limpos, features, previsões, métricas)

Cada integrante mantém a mesma estrutura localmente.

## Estrutura por base

```
data/
├── README.md
├── mae_consolidated.csv              # opcional — todas as bases
├── ljung_box_consolidated.csv        # opcional — todas as bases
├── base_01/
│   ├── [arquivo original].csv        # como fornecido — não renomear
│   ├── cleaned_base_01.csv           # após limpeza
│   ├── features_base_01.parquet      # opcional — matriz de features
│   ├── predictions_sarimax_base_01.csv
│   ├── predictions_holt_winters_base_01.csv
│   ├── predictions_random_forest_base_01.csv
│   ├── predictions_elastic_net_base_01.csv
│   ├── residuals_{modelo}_base_01.csv
│   ├── mae_base_01.csv               # MAE dos 4 modelos nesta base
│   ├── ljung_box_base_01.csv
│   └── hyperparams_{modelo}_base_01.json
├── base_02/
│   └── ...
└── base_05/
```

## Nomenclatura obrigatória

Padrão geral: **`{tipo}_{qualificador}_{base_id}.{ext}`**

| Tipo | Padrão do arquivo | Exemplo |
|------|-------------------|---------|
| Limpo | `cleaned_{base_id}.csv` | `cleaned_base_01.csv` |
| Features | `features_{base_id}.parquet` | `features_base_03.parquet` |
| Previsões OOS | `predictions_{modelo}_{base_id}.csv` | `predictions_sarimax_base_01.csv` |
| Resíduos | `residuals_{modelo}_{base_id}.csv` | `residuals_random_forest_base_02.csv` |
| MAE (por base) | `mae_{base_id}.csv` | `mae_base_04.csv` |
| Ljung-Box (por base) | `ljung_box_{base_id}.csv` | `ljung_box_base_01.csv` |
| Hiperparâmetros | `hyperparams_{modelo}_{base_id}.json` | `hyperparams_elastic_net_base_01.json` |
| MAE global | `mae_consolidated.csv` | em `data/` (raiz) |
| Ljung-Box global | `ljung_box_consolidated.csv` | em `data/` (raiz) |

### Slugs de modelo (`{modelo}`)

`sarimax` · `holt_winters` · `random_forest` · `elastic_net` (especialização grupo 3)

### Regras

- **`base_id`** sempre no formato `base_01` … `base_05` (com zero à esquerda).
- Arquivos **originais fornecidos**: manter nome original; não usar prefixo `cleaned_`.
- **Todo dado gerado** pela pipeline vai em `data/`, nunca em `artifacts/` (pickles ficam em `artifacts/`).
- Preferir `.parquet` para DataFrames grandes; `.csv` para tabelas pequenas e entrega.
- Colunas mínimas em `predictions_*`: `origin_date`, `forecast_date`, `y_true`, `y_pred`, `horizon_step`

## Setup inicial

1. Receber os 5 datasets do professor ou drive compartilhado.
2. Criar `data/base_XX/` e colocar os arquivos originais dentro.
3. No notebook, salvar limpeza como `cleaned_{base_id}.csv`.
4. Modelos treinados → `../artifacts/base_XX/{modelo}.pkl` (ver [`artifacts/README.md`](../artifacts/README.md)).

## Exemplo no notebook

```python
from pathlib import Path
import pandas as pd

BASE_ID = "base_01"
DATA_DIR = Path("../data") / BASE_ID
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Carregar raw
df = pd.read_csv(DATA_DIR / "nome_original.csv")

# Salvar limpo
df_clean = ...
df_clean.to_csv(DATA_DIR / f"cleaned_{BASE_ID}.csv", index=False)

# Salvar previsões
predictions.to_csv(DATA_DIR / f"predictions_sarimax_{BASE_ID}.csv", index=False)
```

## Entrega (zip Odete)

Incluir em `data/`:

- Arquivos originais de cada `base_XX/`
- `cleaned_{base_id}.csv` de cada base
- `mae_consolidated.csv` (e demais consolidados usados no relatório)
