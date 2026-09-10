# SPEC — Avaliação

**Versão:** 0.1  
**ADR relacionadas:** 0001

## 1. Métrica principal — MAE

```python
def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return np.mean(np.abs(y_true - y_pred))
```

- Calculado sobre **todas** as previsões OOS do walk-forward por combinação base × modelo.
- **Não** somar nem tirar média de MAE entre bases.

## 2. Comparação entre modelos

Por base:
1. Tabela MAE dos 4 modelos
2. Ranking (1º = menor MAE)
3. Identificar vencedor

Global (entre bases):
- Contagem de vitórias por modelo
- Posição média no ranking

## 3. Análise de resíduos (por combinação)

| Artefato | Descrição |
|----------|-----------|
| Série temporal dos resíduos | Gráfico ao longo do tempo |
| ACF dos resíduos | Gráfico |
| Ljung-Box | p-valor documentado |

**Resíduo:** `e_t = y_true_t - y_pred_t` (OOS)

Discussão obrigatória: viés, padrões remanescentes, variabilidade, autocorrelação.

> Tabela consolidada Ljung-Box no **corpo principal** do relatório.

## 4. Feature importance

- Random Forest + modelo de especialização
- Destacar variáveis externas e retomar disponibilidade temporal na interpretação

## 5. Saídas (salvar em `data/`)

| Arquivo | Conteúdo |
|---------|----------|
| `data/base_XX/mae_{base_id}.csv` | MAE dos 4 modelos na base |
| `data/mae_consolidated.csv` | MAE de todas as bases |
| `data/base_XX/residuals_{modelo}_{base_id}.csv` | Resíduos OOS |
| `data/base_XX/ljung_box_{base_id}.csv` | Resultados Ljung-Box |
| `data/ljung_box_consolidated.csv` | Tabela consolidada para o relatório |

Gráficos: células do notebook ou export PNG na pasta da base (nome descritivo).

## 6. STL (pré-modelagem, por base)

- Decomposição STL da variável-alvo
- Interpretar tendência, sazonalidade, residual
- Força da sazonalidade (método da disciplina)
