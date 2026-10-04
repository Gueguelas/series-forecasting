# Plano operacional — Base 02 PPC com variáveis exógenas

**Status:** executado e validado em 01/10/2026  
**Base correta:** [`data/PPC_exogenous.csv`](../data/PPC_exogenous.csv)  
**Notebook:** [`notebooks/base_02.ipynb`](../notebooks/base_02.ipynb)  
**Referência estrutural:** [`notebooks/base_05.ipynb`](../notebooks/base_05.ipynb)  
**Grupo do trabalho:** 3 — especialização **Elastic Net**

> “Base 02” identifica o segundo conjunto de dados/notebook. A especialização do grupo continua sendo Elastic Net, conforme a documentação versionada do repositório.

## 1. Objetivo

Prever o preço de abertura (`Open`) da Pilgrim's Pride Corporation no próximo pregão e comparar quatro modelos sob o mesmo protocolo temporal: SARIMAX com regressoras exógenas defasadas, Holt-Winters, Random Forest e Elastic Net.

O notebook deve ser autocontido, reexecutável e produzir previsões, métricas, resíduos, diagnósticos e modelos persistidos sem modificar o CSV original.

## 2. Inventário e contrato temporal

| Item | Definição |
|---|---|
| `BASE_ID` | `base_02` |
| Fonte somente leitura | `data/PPC_exogenous.csv` |
| Período auditado | 25/07/2013 a 16/09/2026 |
| Observações | 3.430 pregões |
| Alvo | `Open` em USD |
| Horizonte | 1 pregão |
| Passo | 1 pregão observado |
| Teste final | últimos 63 pregões |
| Seed | 42 |

Disponibilidade das variáveis:

- OHLCV da PPC: somente valores observados até a origem;
- `TSN_Close`, `XLP_Close`, `CALM_Close` e `USD_MXN`: `lag_only`;
- calendário da data prevista: `known_ahead`;
- nenhuma variável do pregão previsto entra sem defasagem.

## 3. Auditoria e limpeza

- validar esquema, tipos, datas, ausências e duplicatas;
- exigir preços positivos, volume não negativo e consistência OHLC;
- manter somente sessões observadas, sem criar fins de semana ou feriados;
- preservar volumes zero e usar `log1p` quando o volume entrar como feature;
- sinalizar retornos extremos por 3×IQR, sem removê-los;
- salvar a versão validada em `data/base_02/cleaned_base_02.csv`;
- comparar SHA-256 antes e depois para provar que o raw não mudou.

## 4. Diagnóstico temporal

O teste é separado antes de qualquer diagnóstico ou tuning. No desenvolvimento:

- ADF no nível, primeira diferença e retorno do `Open`;
- ACF e PACF nas três transformações;
- STL e força sazonal para `m ∈ {5, 10, 21, 63}`;
- visualização detalhada dos ciclos de 5 e 21 pregões.

## 5. Features e anti-vazamento

Random Forest e Elastic Net usarão o mesmo vetor:

- lags do `Open`: 1, 2, 5, 10, 21, 63 e 252;
- lags 1, 2, 5 e 21 de High, Low, Close, log-volume, TSN, XLP, CALM e USD/MXN;
- médias e desvios móveis do Open em 5, 21, 63 e 252 pregões, após `shift(1)`;
- médias e desvios móveis dos retornos em 5, 21 e 63 pregões, após `shift(1)`;
- mês, fim do mês e codificações cíclicas semanal/anual da data prevista;
- `observed_source_max_date <= origin_date` em todas as amostras.

## 6. Tuning e avaliação

| Modelo | Busca no desenvolvimento |
|---|---|
| SARIMAX | três candidatos semanais selecionados a partir da busca preliminar, com origens expansivas |
| Holt-Winters | tendência ausente/aditiva, amortecimento e sazonalidade aditiva de 5/21 pregões |
| Random Forest | `GridSearchCV` com `TimeSeriesSplit(5)` e grade enxuta para viabilizar o walk-forward local |
| Elastic Net | `StandardScaler` dentro do pipeline, alvo interno `Open - close_lag_1` e `GridSearchCV` com `TimeSeriesSplit(5)` |

Depois do tuning, os parâmetros ficam congelados. Para cada um dos 63 pregões do teste, o treinamento usa apenas amostras cuja `forecast_date <= origin_date`. Os quatro modelos devem produzir exatamente as mesmas chaves OOS e previsões finitas.

## 7. Métricas, resíduos e interpretação

- ranking por MAE OOS;
- observado versus previsto e dispersão por modelo;
- resíduos `observado − previsto`;
- ACF/PACF residual e Ljung–Box nos lags 5 e 10;
- importância nativa e por permutação OOS do Random Forest;
- coeficientes padronizados do Elastic Net;
- coeficientes exógenos do SARIMAX.

## 8. Artefatos

Em `data/base_02/`: `cleaned`, `features`, hiperparâmetros, previsões, resíduos, MAE, Ljung–Box e importância de variáveis.

Em `artifacts/base_02/`: `{modelo}.pkl` e `{modelo}_meta.json` para os quatro modelos.

## 9. Critérios de aceite

- [x] `Restart & Run All` conclui sem estado oculto.
- [x] O raw permanece byte a byte inalterado.
- [x] O esquema possui as dez colunas esperadas e não há ausências/duplicatas.
- [x] Nenhuma feature observada ultrapassa a origem.
- [x] O teste final não entra no tuning.
- [x] Cada modelo gera 63 previsões OOS finitas com chaves idênticas.
- [x] MAE, resíduos e Ljung–Box existem para os quatro modelos.
- [x] Hiperparâmetros, modelos e metadados são persistidos.
- [x] O notebook registra resultados reais da execução e a validação final passa.

### Resultado da execução

| Rank | Modelo | MAE OOS |
|---:|---|---:|
| 1 | Elastic Net | 0,289499 |
| 2 | Random Forest | 0,323001 |
| 3 | SARIMAX | 0,347727 |
| 4 | Holt-Winters | 0,562463 |

- Melhoria incremental: o Elastic Net passou a prever o gap `Open - close_lag_1` e depois reconstruir o preço. A estrutura A-I e os quatro modelos foram mantidos.
- 63 previsões finitas por modelo, de 22/06/2026 a 16/09/2026.
- Chaves OOS idênticas nos quatro modelos.
- Ljung-Box não rejeitou ruído branco nos lags 5 e 10 para nenhum modelo (`p > 0,05`).
- Hash SHA-256 do raw validado: `B008A6DD13CD9E1DA955710745E92DA7C1C19EB9A6D6F7D9D97DE972C571629B`.

## 10. Ordem de execução

1. gerar o notebook adaptado à base PPC;
2. executar todas as células em ambiente isolado;
3. corrigir qualquer falha de dados, convergência ou contrato;
4. reexecutar desde o início;
5. atualizar este plano com o resultado efetivo e marcar os critérios concluídos.
