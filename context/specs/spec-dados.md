# SPEC — Dados

**Versão:** 0.3  
**ADR relacionadas:** 0003, 0004, 0005

## 1. Princípio

Os datasets são **fornecidos ao grupo**. Tudo que for dado — raw ou gerado — fica em `data/`. Modelos `.pkl` ficam em `artifacts/` (ver ADR-0005).

Guia completo: [`data/README.md`](../../data/README.md)

## 2. Layout (`data/`)

```
data/
├── mae_consolidated.csv
├── ljung_box_consolidated.csv
├── base_01/
│   ├── [arquivo original].csv
│   ├── cleaned_base_01.csv
│   ├── features_base_01.parquet
│   ├── predictions_sarimax_base_01.csv
│   ├── predictions_holt_winters_base_01.csv
│   ├── predictions_random_forest_base_01.csv
│   ├── predictions_elastic_net_base_01.csv
│   ├── residuals_{modelo}_base_01.csv
│   ├── mae_base_01.csv
│   ├── ljung_box_base_01.csv
│   └── hyperparams_{modelo}_base_01.json
└── base_02/ … base_05/
```

## 2.1 Nomenclatura (resumo)

| Tipo | Padrão |
|------|--------|
| Limpo | `cleaned_{base_id}.csv` |
| Features | `features_{base_id}.parquet` |
| Previsões | `predictions_{modelo}_{base_id}.csv` |
| Resíduos | `residuals_{modelo}_{base_id}.csv` |
| MAE | `mae_{base_id}.csv` ou `mae_consolidated.csv` |
| Ljung-Box | `ljung_box_{base_id}.csv` |
| Hiperparâmetros | `hyperparams_{modelo}_{base_id}.json` |

Slugs: `sarimax`, `holt_winters`, `random_forest`, `elastic_net`

## 3. Bases (5 comuns à turma)

| Pasta | Nome do dataset | Arquivo(s) | Período | Frequência | Status |
|-------|-----------------|------------|---------|------------|--------|
| `base_01/` | [DEFINIR] | | | | Aguardando |
| `base_02/` | [DEFINIR] | | | | Aguardando |
| `base_03/` | [DEFINIR] | | | | Aguardando |
| `base_04/` | [DEFINIR] | | | | Aguardando |
| `base_05/` | [DEFINIR] | | | | Aguardando |

## 4. Carregamento e persistência no notebook

```python
from pathlib import Path

BASE_ID = "base_01"
DATA_DIR = Path("../data") / BASE_ID

# Raw (nome original fornecido)
df = pd.read_csv(DATA_DIR / "nome_original.csv")

# Limpo — nomenclatura obrigatória
df_clean.to_csv(DATA_DIR / f"cleaned_{BASE_ID}.csv", index=False)

# Previsões
preds.to_csv(DATA_DIR / f"predictions_sarimax_{BASE_ID}.csv", index=False)
```

> Executar notebooks com working directory em `notebooks/` (padrão do Jupyter ao abrir o arquivo de lá).

## 5. Dicionário de variáveis (por base)

Documentar no início do notebook correspondente (`notebooks/base_XX.ipynb`):

| Coluna | Tipo | Descrição | Alvo/Externa | Disponibilidade na previsão |
|--------|------|-----------|--------------|----------------------------|
| `target` | float | | Alvo | — |
| `ext_*` | | | Externa | Conhecida / Lag / Previsão / Excluída |

**Disponibilidade** (ADR-0003): `known_ahead` | `forecast_at_origin` | `lag_only` | `excluded`

## 6. EDA obrigatório (no notebook da base)

- [ ] Gráfico da série-alvo
- [ ] Gráficos das principais variáveis externas
- [ ] Valores ausentes (contagem e padrão temporal)
- [ ] Duplicidades de timestamp
- [ ] Irregularidades temporais
- [ ] Outliers (método documentado)

## 7. Limpeza e transformação

Documentar em células markdown do notebook:

| Etapa | Decisão | Justificativa |
|-------|---------|---------------|
| Regularização de frequência | | |
| Tratamento de missing | | |
| Tratamento de outliers | | |
| Transformação do alvo (log, etc.) | | |

## 8. Entrega (zip Odete)

Incluir as 5 pastas `data/base_XX/` com os arquivos utilizados, ou indicação clara das fontes conforme enunciado.
