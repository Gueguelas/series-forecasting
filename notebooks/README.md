# Notebooks — entregas do projeto

Toda a análise e o relatório são feitos em **Jupyter notebooks**. Um notebook por dataset + um notebook de relatório consolidado.

## Mapa notebook ↔ dataset

| Notebook | Dados | Responsável |
|----------|-------|-------------|
| `base_01.ipynb` | `../data/base_01/` | [DEFINIR] |
| `base_02.ipynb` | `../data/base_02/` | [DEFINIR] |
| `base_03.ipynb` | `../data/base_03/` | [DEFINIR] |
| `base_04.ipynb` | `../data/base_04/` | [DEFINIR] |
| `base_05.ipynb` | `../data/base_05/` | [DEFINIR] |
| `relatorio.ipynb` | Consolida os 5 acima | [DEFINIR] |

## Conteúdo esperado por `base_XX.ipynb`

Cada notebook deve ser **autocontido e reprodutível** para a sua base:

1. Carregamento e documentação do dataset
2. EDA, limpeza e dicionário de variáveis
3. Decomposição STL e força da sazonalidade
4. Feature engineering (anti-leakage)
5. Otimização de hiperparâmetros (4 modelos)
6. Validação walk-forward
7. MAE e comparação dos 4 modelos na base
8. Análise de resíduos (gráfico, ACF, Ljung-Box)
9. Feature importance (RF + modelo de especialização)

## `relatorio.ipynb`

- Narrativa comparativa entre as 5 bases
- Tabelas consolidadas (MAE, Ljung-Box)
- Estudo aprofundado do modelo de especialização
- Export HTML paginado + PDF
- Apêndice com registro de demandas

## Convenções

- Abrir/executar notebooks a partir desta pasta (`notebooks/`) para caminhos relativos funcionarem.
- Primeira célula: `BASE_ID`, `DATA_DIR`, `ARTIFACT_DIR`, imports, `random_state`.
- **Dados derivados** → `../data/base_XX/` (`cleaned_{base_id}.csv`, `predictions_*`, etc.)
- **Modelos treinados** → `../artifacts/base_XX/{modelo}.pkl`
- Nomenclatura completa: [`data/README.md`](../data/README.md) · [`artifacts/README.md`](../artifacts/README.md)
- Seções em markdown alinhadas ao enunciado ([`context/specs/spec-relatorio.md`](../context/specs/spec-relatorio.md)).

## Setup

```bash
# Na raiz do projeto
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # quando disponível
jupyter lab notebooks/
```
