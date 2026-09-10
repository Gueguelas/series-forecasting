# ADR-0005: Persistência de artifacts e nomenclatura em `data/`

**Status:** Aceita  
**Data:** 2026-09-10  
**Relacionado:** [ADR-0004](0004-estrutura-repositorio.md)

## Contexto

Os notebooks treinam modelos e geram dados intermediários (limpos, previsões, métricas). É preciso padronizar **onde** e **como nomear** esses arquivos para reprodutibilidade e colaboração entre integrantes.

## Decisão

### 1. Pasta `artifacts/` — modelos treinados (pickles)

- Caminho: `artifacts/{base_id}/{modelo}.pkl`
- Metadados: `artifacts/{base_id}/{modelo}_meta.json`
- Gitignored (exceto `artifacts/README.md`)
- Biblioteca preferida: `joblib` (sklearn); `pickle` para statsmodels quando necessário

### 2. Pasta `data/` — todo dado tabular

Qualquer arquivo de dados gerado ou recebido fica em `data/`:

| Categoria | Padrão |
|-----------|--------|
| Raw (fornecido) | `data/base_XX/{nome_original}` — sem renomear |
| Limpo | `data/base_XX/cleaned_{base_id}.csv` |
| Features | `data/base_XX/features_{base_id}.parquet` |
| Previsões | `data/base_XX/predictions_{modelo}_{base_id}.csv` |
| Resíduos | `data/base_XX/residuals_{modelo}_{base_id}.csv` |
| MAE por base | `data/base_XX/mae_{base_id}.csv` |
| Ljung-Box | `data/base_XX/ljung_box_{base_id}.csv` |
| Hiperparâmetros | `data/base_XX/hyperparams_{modelo}_{base_id}.json` |
| Consolidados | `data/mae_consolidated.csv`, `data/ljung_box_consolidated.csv` |

### 3. Slugs de modelo

`sarimax` · `holt_winters` · `random_forest` · `elastic_net`

### 4. Separação de responsabilidades

| Pasta | Conteúdo |
|-------|----------|
| `data/` | CSV, Parquet, JSON de dados e métricas |
| `artifacts/` | Apenas `.pkl` de modelos + `_meta.json` |
| `notebooks/` | Código e narrativa (versionado no git) |

## Consequências

- Notebooks devem usar caminhos relativos `../data/` e `../artifacts/`
- Guias detalhados: [`data/README.md`](../../data/README.md), [`artifacts/README.md`](../../artifacts/README.md)
- Zip Odete inclui `data/` (derivados relevantes) e opcionalmente `artifacts/`
