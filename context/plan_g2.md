# Plano operacional — Notebook 2 (`base_02`)

**Status:** Executado e validado em 26/09/2026  
**Base:** DailyClimate (Delhi)  
**Grupo do trabalho:** 3 — especialização **Elastic Net**  
**Notebook:** [`notebooks/base_02.ipynb`](../notebooks/base_02.ipynb)  
**Dados:** [`data/base_02/DailyClimate.csv`](../data/base_02/DailyClimate.csv)  
**Notebook de referência estrutural:** [`notebooks/base_05.ipynb`](../notebooks/base_05.ipynb)

> “Grupo 2” neste plano identifica a segunda base/notebook. O modelo de especialização continua sendo Elastic Net, conforme o PRD do Grupo 3.

---

## 1. Objetivo e escopo

Construir um notebook autocontido e reprodutível para prever `meantemp` um dia à frente, cobrindo documentação, EDA, limpeza, decomposição STL, feature engineering, tuning temporal, avaliação walk-forward, MAE, resíduos, Ljung–Box, importância de variáveis e persistência dos quatro modelos:

1. SARIMAX com variáveis exógenas disponíveis na origem;
2. Holt-Winters univariado;
3. Random Forest;
4. Elastic Net, especialização do grupo.

O notebook segue a organização A–I da `base_05`, mas todas as hipóteses de mercado financeiro foram substituídas por decisões próprias da série climática diária.

---

## 2. Inventário da base

| Item | Definição |
|---|---|
| `BASE_ID` | `base_02` |
| Arquivo raw | `DailyClimate.csv` |
| Período bruto | 2013-01-01 a 2017-04-24 |
| Frequência | diária |
| Alvo | `meantemp` (°C) |
| Externas | `humidity` (%), `wind_speed` (km/h), `meanpressure` (hPa) |
| Horizonte | 1 dia |
| Passo entre origens | 1 dia |
| Teste final | últimos 63 dias limpos |
| Seed | 42 |

### Disponibilidade temporal

As três variáveis meteorológicas externas são tratadas como `lag_only`: o valor observado no dia previsto não está disponível na origem. Somente lags observados até `origin_date` entram em SARIMAX, Random Forest e Elastic Net. Calendário da data prevista é `known_ahead`.

---

## 3. Decisões de qualidade e limpeza

O raw é preservado. A limpeza gera `cleaned_base_02.csv`.

| Problema | Decisão | Justificativa |
|---|---|---|
| Data duplicada em 2017-01-01 | preferir o registro cuja pressão esteja no intervalo físico de 900–1100 hPa; em empate, manter o último | regra determinística baseada em integridade multivariada |
| Pressão fora de 900–1100 hPa | converter em ausente e preencher apenas com `ffill` | valores como -3 e 7679 hPa são erros de medição; `ffill` não consulta o futuro |
| Demais ausências | falhar se restarem após a limpeza | impede treinamento silencioso com dados incompletos |
| Frequência | exigir diferença de exatamente um dia após deduplicação | não inventar datas nem interpolar o alvo |
| Outliers de temperatura | sinalizar por 3×IQR da primeira diferença, sem remover | extremos climáticos podem ser reais |
| Escala do alvo | manter °C | MAE diretamente interpretável |

---

## 4. Separação temporal e sazonalidade

- O teste final é separado antes de qualquer tuning.
- O desenvolvimento termina antes dos últimos 63 dias.
- ADF, ACF, PACF e força de sazonalidade usam somente o desenvolvimento.
- STL compara `m ∈ {7, 30, 365}` para ciclos semanal, aproximadamente mensal e anual.
- O SARIMAX investiga sazonalidade semanal (`m=7`); o ciclo anual é representado também por seno/cosseno do dia do ano para evitar um estado sazonal SARIMAX excessivamente grande.
- Holt-Winters investiga sazonalidade semanal e anual quando a configuração converge.

---

## 5. Features e contrato anti-vazamento

Random Forest e Elastic Net usam exatamente o mesmo vetor:

- lags do alvo: 1, 2, 3, 7, 14, 30 e 365 dias;
- lags das externas: 1, 2, 7 e 30 dias;
- médias e desvios móveis do alvo em 7, 30 e 365 dias, sempre após `shift(1)`;
- mudança da temperatura em 1 e 7 dias, calculada apenas com passado;
- calendário da data prevista: mês, dia da semana e dia do ano;
- codificação cíclica semanal e anual.

As primeiras linhas incompletas são descartadas. O notebook mantém `observed_source_max_date` para provar que nenhuma observação usada ultrapassa a origem. O scaler do Elastic Net fica dentro de `Pipeline` e é ajustado somente no treino de cada fold/origem.

---

## 6. Tuning e avaliação

| Modelo | Procedimento no desenvolvimento |
|---|---|
| SARIMAX | grid temporal expansivo de `(p,d,q)` e termos sazonais semanais |
| Holt-Winters | tendência ausente/aditiva, amortecimento, sazonalidade e período; tendência multiplicativa excluída após instabilidade numérica no walk-forward |
| Random Forest | `GridSearchCV` + `TimeSeriesSplit(5)` |
| Elastic Net | `GridSearchCV` + `TimeSeriesSplit(5)` com `StandardScaler` |

Os hiperparâmetros selecionados são congelados antes do teste. Para cada dia do teste:

1. usar apenas amostras com `forecast_date <= origin_date`;
2. reajustar o modelo;
3. prever o dia seguinte;
4. registrar datas, observado, previsto e tempos;
5. exigir chaves OOS idênticas nos quatro modelos.

---

## 7. Estrutura do notebook

- **Introdução e setup:** identidade, caminhos, seed e versões.
- **A–C:** documentação, integridade, EDA e limpeza.
- **D:** ADF, ACF/PACF, STL e força da sazonalidade.
- **E:** features, persistência Parquet e auditoria anti-vazamento.
- **F:** tuning temporal e motor walk-forward.
- **G:** MAE, ranking e gráficos OOS.
- **H:** resíduos, ACF/PACF, histogramas e Ljung–Box.
- **I:** importância, interpretação e modelos finais.
- **Validação final:** contratos, arquivos obrigatórios e preservação do raw.

---

## 8. Artefatos esperados

### `data/base_02/`

- `cleaned_base_02.csv`
- `features_base_02.parquet`
- `hyperparams_{modelo}_base_02.json`
- `predictions_{modelo}_base_02.csv`
- `residuals_{modelo}_base_02.csv`
- `mae_base_02.csv`
- `ljung_box_base_02.csv`

### `artifacts/base_02/`

- `{modelo}.pkl`
- `{modelo}_meta.json`

`{modelo}` ∈ `sarimax`, `holt_winters`, `random_forest`, `elastic_net`.

---

## 9. Critérios de aceite

- [x] `Restart & Run All` conclui sem estado oculto.
- [x] O raw permanece byte a byte inalterado.
- [x] A série limpa possui datas únicas, ordenadas e diárias.
- [x] Não restam valores ausentes ou pressões fora do intervalo definido.
- [x] Features observadas têm `observed_source_max_date <= origin_date`.
- [x] RF e Elastic Net usam as mesmas features.
- [x] Tuning não acessa o teste final.
- [x] Os quatro arquivos de previsão possuem as mesmas chaves e 63 previsões.
- [x] Todas as 63 previsões de cada modelo são finitas; nenhum `NaN` pode ser ignorado no MAE ou no Ljung–Box.
- [x] MAE é calculado somente sobre previsões OOS.
- [x] Resíduos e Ljung–Box existem para os quatro modelos.
- [x] Hiperparâmetros, modelos e metadados são persistidos com a nomenclatura do repositório.
- [x] A conclusão textual é revisada após a execução e reflete os resultados efetivamente obtidos.

### Resultado da execução

| Rank | Modelo | MAE OOS (°C) |
|---:|---|---:|
| 1 | SARIMAX | 1,256775 |
| 2 | Random Forest | 1,256998 |
| 3 | Holt-Winters | 1,301291 |
| 4 | Elastic Net | 1,442940 |

- 63 previsões finitas por modelo, de 21/02/2017 a 24/04/2017.
- Nenhum Ljung–Box rejeitou ruído branco nos lags 7 e 14 (`p>0,05`).
- Força sazonal: anual `0,933`, mensal `0,250`, semanal `0,041`.
- Validação final: 17 arquivos de dados e 8 artefatos de modelo.

---

## 10. Ordem de execução

1. Executar o notebook inteiro em ambiente com Python e dependências instaladas.
2. Revisar avisos/convergência dos modelos estatísticos.
3. Conferir tabelas de sazonalidade, MAE e Ljung–Box.
4. Atualizar a interpretação textual apenas se os outputs contradisserem as hipóteses descritas.
5. Revisar os arquivos gerados e somente então preparar consolidação/relatório.
