# Plano operacional — Notebook 1 (`base_01`)

**Status:** Vigente para a branch `grupo-1`  
**Responsável desta base:** integrante da branch `grupo-1`  
**Grupo do trabalho:** 3 — especialização **Elastic Net** (não confundir com o Grupo 1 do enunciado, que usa XGBoost — `base_01` é o número do *dataset*, não do grupo de especialização)  
**Notebook:** [`notebooks/base_01.ipynb`](../notebooks/base_01.ipynb) (a criar na implementação)  
**Dados:** Daily Delhi Climate → pasta [`data/base_01/`](../data/README.md)  
**Enunciado:** [`docs/instrucoes.pdf`](../docs/instrucoes.pdf)  
**Specs aplicáveis:** dados, features, validação, modelos, avaliação — só o recorte desta base  
**Referência metodológica:** notebooks de aula em [`document-reference/grupo1/`](../document-reference/grupo1/) (`Pipeline SARIMAX.ipynb`, `4 - HoltWinters.ipynb`) — usados para a **técnica** (split sem vazamento, força de sazonalidade via STL, grid search paralelo, diagnóstico de resíduos), não para os dados (eles usam séries diferentes, só de exemplo)

Este documento é a receita para **uma** das cinco bases. Cada integrante implementa o pipeline completo na sua base. Os artefatos em `data/base_01/` alimentam depois o `relatorio.ipynb` do grupo; **este plano não cobre** as bases 2–5, o relatório consolidado, a apresentação oral nem o zip Odete.

---

## 0. Como usar este plano

### Precedência

1. Instrução explícita do integrante
2. `docs/instrucoes.pdf`
3. ADRs em `context/adr/`
4. `PRD.md` / `SDD.md`
5. SPECs
6. `RULES.md` / `AGENTS.md`

### O que este notebook precisa cumprir (PDF, uma base)

| Etapa do PDF | O que fazer em `base_01.ipynb` |
|--------------|--------------------------------|
| §5.1 | Documentar, explorar, limpar a série climática de Delhi |
| §5.2 | STL do alvo (`meantemp`) + força da sazonalidade |
| §5.3 | Features sem vazamento; mesmo vetor em RF e Elastic Net |
| §5.4–5.6 | Walk-forward com mesmas origens/horizonte para os 4 modelos; HP fixos no teste |
| §6 | MAE OOS e ranking **dentro desta base** |
| §7 | Resíduos, ACF, Ljung-Box por modelo |
| §8 | Importância: RF + Elastic Net; SARIMAX por coeficientes; HW sem FI tabular |

### Princípios (ADRs)

- **ADR-0001:** MAE só em previsões fora da amostra. Não agregar MAE com outras bases neste notebook.
- **ADR-0002:** walk-forward; mesmas origens, `h` e teste para os quatro modelos **desta** base.
- **ADR-0003:** nenhuma feature usa valor observado depois da `origin_date`.
- **ADR-0004:** lógica no notebook (sem pacote `src/`); caminhos relativos a `notebooks/`.
- **ADR-0005:** CSVs/parquet/JSON em `data/base_01/`; pickles em `artifacts/base_01/`.

### Proibições

- Commit ou push sem pedido explícito
- Usar o período de teste final para escolher hiperparâmetros
- Holt-Winters com variáveis externas
- `humidity` / `wind_speed` / `meanpressure` **da própria data prevista** usados como exógena "conhecida" do SARIMAX ou como feature contemporânea em RF/Elastic Net (vazamento — são variáveis climáticas, não se sabe a umidade/vento/pressão de um dia futuro; só seus **lags** são válidos)
- Preencher datas ausentes inventando observações não documentadas
- Alterar os arquivos raw

Código e nomes de variáveis em **inglês**. Narrativa do notebook em **português**. `random_state = 42` salvo decisão documentada.

---

## 1. Identidade, pastas e célula 0

| Item | Valor |
|------|--------|
| `BASE_ID` | `"base_01"` |
| Raw (nomes originais, não renomear) | `data/base_01/DailyDelhiClimateTrain_grupo1.csv`, `data/base_01/DailyDelhiClimateTest_grupo1.csv` |
| Situação atual | os dois CSVs (e `GRUPO1.md`) ainda estão em `data/` (raiz) — **primeiro passo da implementação** é colocá-los em `data/base_01/` |
| Notebook | `notebooks/base_01.ipynb` |
| Working directory | pasta `notebooks/` (padrão do Jupyter ao abrir o arquivo dali) |

Célula 0 (obrigatória):

```python
from pathlib import Path
import numpy as np
import pandas as pd

BASE_ID = "base_01"
RANDOM_STATE = 42
DATA_DIR = Path("../data") / BASE_ID
ARTIFACT_DIR = Path("../artifacts") / BASE_ID
RAW_TRAIN_FILE = DATA_DIR / "DailyDelhiClimateTrain_grupo1.csv"
RAW_TEST_FILE = DATA_DIR / "DailyDelhiClimateTest_grupo1.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(RANDOM_STATE)
```

Funções auxiliares (MAE, walk-forward, scaler por fold, persistência, Ljung-Box, força da sazonalidade) podem viver **no próprio notebook** ou, se o grupo criar, em `notebooks/ts_common.py` importado daqui. Não criar `src/`.

### Bibliotecas previstas

Python 3.11+ (SDD). Uso neste notebook: `pandas`, `numpy`, `matplotlib`, `seaborn`, `statsmodels` (STL, SARIMAX, Ljung-Box, ACF), `scikit-learn` (Random Forest, Elastic Net, `StandardScaler`, permutation importance), `joblib` (grid search paralelo, no padrão do `Pipeline SARIMAX.ipynb` de referência — `Parallel`/`delayed`/`parallel_config` com `backend="loky"`), `pyarrow` (parquet). Pinagem de versões: quando o repo tiver `requirements.txt`.

---

## 2. Definição da série (documentar no início do notebook)

### 2.1 Inventário

| Campo | Valor proposto |
|-------|----------------|
| Nome | Daily Climate Time Series — Delhi |
| Arquivos | `DailyDelhiClimateTrain_grupo1.csv` + `DailyDelhiClimateTest_grupo1.csv` (contíguos: treino até 2016-12-31, teste a partir de 2017-01-01) |
| Colunas | `date`, `meantemp`, `humidity`, `wind_speed`, `meanpressure` |
| Linhas | ~1461 (treino) + ~114 (teste) |
| Período | 2013-01-01 → 2017-04-24 |
| Frequência | Diária (`D`) |
| Unidade do alvo | Temperatura média diária (°C) |
| Alvo | `meantemp` |
| Externas | `humidity` (%), `wind_speed` (km/h), `meanpressure` (unidade suspeita — ver Seção C) — atende ao mínimo de 2 externas do PDF §4 |

Fonte a citar no notebook: Kaggle — [Daily Climate time series data](https://www.kaggle.com/datasets/sumanthvrao/daily-climate-time-series-data) (sumanthvrao, CC0-1.0), já documentada em [`data/GRUPO1.md`](../data/GRUPO1.md).

### 2.2 Dicionário e disponibilidade (ADR-0003)

Hipótese de previsão: na origem `t` (última data com observação conhecida), prever `meantemp` dos **próximos `h` dias**.

| Coluna | Papel | Disponibilidade | Tratamento |
|--------|--------|-----------------|------------|
| `date` | Índice | `known_ahead` | Datetime diário |
| `meantemp` | Alvo | — | Lags e janelas só até `t` |
| `humidity`, `wind_speed`, `meanpressure` | Externas | **`lag_only`** | Não são conhecidas com antecedência (não se sabe a umidade/vento/pressão de um dia futuro sem um forecast meteorológico próprio, fora do escopo). Usar apenas seus valores em `≤ t` (lags), nunca o valor do dia previsto |
| Dia do ano, mês, estação do ano | Calendário | `known_ahead` | Valor da **data prevista** (determinístico) |

**Vazamento clássico a recusar:** diferente do notebook de referência SARIMAX (onde `temperatura` e `feriado` são exógenas legitimamente conhecidas com antecedência para prever vendas), aqui `humidity`/`wind_speed`/`meanpressure` **são** variáveis meteorológicas tão "futuras" quanto o próprio alvo. Usar o valor do dia `t+k` (`k≥1`) dessas colunas como exógena do SARIMAX ou feature de RF/Elastic Net para prever `meantemp` de `t+k` é vazamento. Regra: toda externa entra como **lag** (ex.: `humidity_lag_1`), nunca como valor contemporâneo ao horizonte previsto.

### 2.3 Horizonte e walk-forward (desta base)

O `h` **global das cinco bases** é decisão do grupo (fora do escopo deste plano). **Neste notebook**, escolher e **documentar** um `h` em dias corridos.

| Parâmetro | Proposta inicial | Como fechar |
|-----------|------------------|--------------|
| Período de teste | Fronteira já definida pelo Kaggle: 2017-01-01 a 2017-04-24 (~114 dias) — adotar como período de teste **congelado**, análogo ao "últimos 20%" do notebook de referência SARIMAX | Não usar para tuning |
| `horizon` (`h`) | `7` dias (uma semana) | Justificar no markdown; usar o mesmo `h` nos 4 modelos |
| `origin_step` | `7` dias (origens não sobrepostas, ~16 origens no período de teste) | Ajustar para `1` dia (origens diárias sobrepostas) se o grupo quiser mais pontos de avaliação — documentar a escolha |
| `train_min_obs` | Todo o treino disponível até a origem (≥ ~3 anos antes da 1ª origem de teste) | Ajustar após EDA/STL se a série for curta demais para o `m` sazonal escolhido |
| Validação interna (tuning) | Últimos ~20% do treino (ex.: ano de 2016), no mesmo espírito do `subtreino`/`validação` do notebook de referência SARIMAX | Escolher HP fixos antes de tocar no período de teste |

Todos os modelos desta base: **mesmo** `h`, mesmas `origin_date`, mesmo conjunto de pares `(origin, forecast_date)`.

**Aceite de conformidade:** os quatro CSVs `predictions_*_base_01.csv` têm o **mesmo número de linhas** e o mesmo conjunto de `(origin_date, forecast_date, horizon_step)`.

---

## 3. Estrutura do notebook (checklist de aceite)

Espelhar [`specs/spec-relatorio.md`](specs/spec-relatorio.md) §2 e [`notebooks/README.md`](../notebooks/README.md).

### Seção A — Setup

- [ ] Célula 0 (caminhos, seed, versões impressas: pandas, sklearn, statsmodels)
- [ ] Conferir `RAW_TRAIN_FILE.exists()` e `RAW_TEST_FILE.exists()`

### Seção B — Documentação e EDA (§5.1)

- [ ] Texto: fonte, descrição, período, frequência, unidade, significado de cada coluna
- [ ] Tabela-dicionário com coluna `availability`
- [ ] Gráfico da série `meantemp`
- [ ] Gráficos de `humidity`, `wind_speed`, `meanpressure`
- [ ] Contagem e padrão temporal de missing
- [ ] Duplicidade de timestamp
- [ ] Irregularidades: gaps na frequência diária
- [ ] Outliers: método documentado (ex.: IQR / z-score robusto), com atenção especial a `meanpressure` (valores já sinalizados como suspeitos em `GRUPO1.md`, ex. `59.0` misturado com valores ~1000+)

### Seção C — Limpeza

Tabela markdown obrigatória:

| Etapa | Decisão | Justificativa |
|-------|---------|----------------|
| Parse de `date` | `pd.to_datetime`; ordenar; índice; `asfreq("D")` | Regularizar a frequência diária |
| Concatenação treino+teste | Unir os dois arquivos em uma série contínua, guardando a fronteira 2017-01-01 para o split | Evita reimplementar a divisão do Kaggle |
| Missing | | |
| Outliers de `meanpressure` | Clipar/winsorizar ou tratar como ausente + imputar (decidir e justificar) | Valores fisicamente implausíveis já documentados |
| Outliers de `wind_speed`/`humidity` | | |
| Transformação do alvo | Nível em °C **ou** log; se log, MAE do relatório deve ser desfeito antes de comparar (preferir nível original) | Comparação justa |

- [ ] Salvar `data/base_01/cleaned_base_01.csv` **sem** alterar os raws

### Seção D — STL e sazonalidade (§5.2)

- [ ] STL de `meantemp`
- [ ] Período sazonal `m`: comparar força de sazonalidade (mesmo método do notebook de referência SARIMAX, Seção 4) entre candidatos compatíveis com dado diário — ex. `m=7` (semanal), `m=30` (mensal), `m=365` (anual, esperado vencedor para clima)
- [ ] **Decisão em aberto a documentar:** SARIMA/SARIMAX sazonal completo com `m=365` é computacionalmente caro (grid search pode não convergir em tempo hábil). Se `m=365` vencer a força de sazonalidade mas for inviável no grid search, documentar a alternativa: usar termos de Fourier (harmônicos anuais, `sin`/`cos` de `dia_do_ano/365`) como exógenas do SARIMAX em vez de `seasonal_order` literal com `m=365`, mantendo Holt-Winters com o `m` sazonal diretamente (ele lida melhor com sazonalidade longa que o SARIMA em grade)
- [ ] Interpretar tendência, sazonalidade e resíduo
- [ ] Força da sazonalidade (método da disciplina):

\[
F_s = \max\left(0,\ 1 - \frac{\mathrm{Var}(R)}{\mathrm{Var}(S+R)}\right)
\]

onde `S` e `R` vêm do STL.

### Seção E — Feature engineering (§5.3, ADR-0003)

Conjunto **tabular único** para Random Forest e Elastic Net. Exemplos mínimos:

| Categoria | Exemplos | Regra |
|-----------|----------|--------|
| Lags do alvo | `meantemp_lag_1`, `meantemp_lag_7`, `meantemp_lag_365` | Só passado relativo à origem |
| Lags de externas | `humidity_lag_1`, `wind_speed_lag_1`, `meanpressure_lag_1` | `lag_only` — nunca o valor do dia previsto (Seção 2.2) |
| Janelas | média/desvio móvel de `meantemp` em 7 e 30 dias | Janela **fechada no passado** (shift 1 antes do rolling) |
| Calendário | `day_of_year`, `month`, `season` | `known_ahead` na data **prevista** |
| Cíclico | `sin/cos` do dia do ano (`period=365`) e do dia da semana (`period=7`) | Captura sazonalidade anual/semanal sem exigir `m=365` no modelo |

NaNs do início da série: **drop** das primeiras linhas no treino (preferencial). Forward-fill só com justificativa e sem olhar o futuro.

- [ ] Lista markdown das features finais e parâmetros (lags, janelas)
- [ ] Checklist anti-leakage da spec de features
- [ ] `data/base_01/features_base_01.parquet`

**SARIMAX:** exógenas = lags de `humidity`/`wind_speed`/`meanpressure` (nunca contemporâneas) e/ou termos de Fourier de calendário. **Holt-Winters:** somente `meantemp`.

**Scaler:** `StandardScaler` (e qualquer normalização) com `fit` **apenas** no treino de cada origem do walk-forward. Elastic Net **exige** padronização.

### Seção F — Hiperparâmetros (§5.5) e walk-forward (§5.4–5.6)

Espaço mínimo a investigar (documentar grid/random, ranges, procedimento **no treino**, valores finais, justificativa):

| Modelo | Slug | Investigar |
|--------|------|-------------|
| SARIMAX | `sarimax` | `(p,d,q)`, `(P,D,Q)`, `m`, AIC/BIC, quais exógenas (lags climáticos e/ou Fourier) |
| Holt-Winters | `holt_winters` | trend, seasonal, damped, `m`, suavização |
| Random Forest | `random_forest` | `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`, `max_features` |
| Elastic Net | `elastic_net` | `alpha`, `l1_ratio` + pipeline com scaler |

Loop walk-forward (mesmo padrão do `spec-validacao.md` e do notebook de referência SARIMAX, seções 6–9):

```
Para cada origin_date nas origens de teste:
    train = observações com timestamp <= origin_date
    ajustar modelo com HP já escolhidos (fixos)
    y_hat = previsão dos próximos h dias
    registrar origin_date, forecast_date, y_true, y_pred, horizon_step, tempo
```

- [ ] Mesmas origens para os 4 modelos
- [ ] Sem acesso a dados após `origin_date` em treino/features
- [ ] Registrar tempo de execução por combinação (grid search pode ser caro — usar `joblib.Parallel` como no notebook de referência)

### Seção G — MAE e ranking (§6, só esta base)

```python
mae = np.mean(np.abs(y_true - y_pred))
```

- [ ] MAE sobre **todas** as previsões OOS de cada modelo
- [ ] Tabela dos 4 MAEs + ranking (1º = menor MAE)
- [ ] Discutir por que o vencedor faz sentido nesta série (sazonalidade anual forte esperada, tendência fraca, etc.)
- [ ] `data/base_01/mae_base_01.csv`

Não calcular "MAE médio das cinco bases" aqui.

### Seção H — Resíduos (§7)

Para cada modelo: `e = y_true - y_pred` (OOS).

- [ ] Série temporal dos resíduos
- [ ] ACF
- [ ] Ljung-Box + p-valor interpretado
- [ ] Texto: viés, padrões, variabilidade, autocorrelação
- [ ] `residuals_{modelo}_base_01.csv`
- [ ] `ljung_box_base_01.csv`

### Seção I — Importância (§8)

| Modelo | Método neste notebook |
|--------|-------------------------|
| SARIMAX | Coeficientes, sinal, magnitude, significância |
| Holt-Winters | Nível, tendência, sazonalidade (sem FI) |
| Random Forest | Importância nativa **e/ou** permutation |
| Elastic Net | Coeficientes **após** padronização; destacar o que foi zerado (`l1_ratio`) |

Retomar no texto se as externas (lags de umidade/vento/pressão) realmente ajudam a prever temperatura e se estavam disponíveis na origem.

---

## 4. Persistência (ADR-0005) — só `base_01`

### 4.1 Dados (`data/base_01/`)

| Arquivo | Conteúdo |
|---------|----------|
| `DailyDelhiClimateTrain_grupo1.csv`, `DailyDelhiClimateTest_grupo1.csv` | Raw, nomes originais |
| `cleaned_base_01.csv` | Série limpa e unificada |
| `features_base_01.parquet` | Matriz de features |
| `predictions_{modelo}_base_01.csv` | OOS; colunas mínimas: `origin_date`, `forecast_date`, `y_true`, `y_pred`, `horizon_step` |
| `residuals_{modelo}_base_01.csv` | Resíduos OOS |
| `mae_base_01.csv` | MAE dos 4 modelos |
| `ljung_box_base_01.csv` | Teste por modelo |
| `hyperparams_{modelo}_base_01.json` | Espaço de busca + valores finais |

`{modelo}` ∈ `sarimax` | `holt_winters` | `random_forest` | `elastic_net`

**Não** é obrigação deste notebook gerar `data/mae_consolidated.csv` (relatório do grupo).

### 4.2 Modelos (`artifacts/base_01/`)

Após HP finais, para cada slug:

- `{modelo}.pkl` — `joblib` para sklearn; `pickle` para statsmodels se necessário
- `{modelo}_meta.json` — `base_id`, `model`, `hyperparams`, `trained_at` (UTC), `random_state`, versões de libs

Exemplo de nomes: `artifacts/base_01/elastic_net.pkl`, `artifacts/base_01/elastic_net_meta.json`.

---

## 5. Elastic Net nesta base (estudo local)

O relatório do grupo aprofundará o algoritmo (PDF §9). Neste notebook, o mínimo para não entregar "só `.fit()`":

1. Intuição: mistura L1/L2; `l1_ratio=1` ≈ Lasso, `l1_ratio=0` ≈ Ridge.
2. Por que padronizar (coeficientes comparáveis; `alpha` não-invariante à escala).
3. HP escolhidos e efeito observado (esparsidade vs. shrinkage).
4. Comparar MAE com RF **na mesma matriz de features**.
5. Interpretar coeficientes padronizados à luz de `lag_only` — ex.: quanto pesa `humidity_lag_1` ou os termos de Fourier anuais vs. os próprios lags de `meantemp`.

---

## 6. Ordem de implementação

1. Mover `data/DailyDelhiClimateTrain_grupo1.csv`, `data/DailyDelhiClimateTest_grupo1.csv` e `data/GRUPO1.md` → `data/base_01/`; criar `artifacts/base_01/`.
2. Criar `notebooks/base_01.ipynb` com célula 0 e seções A–I.
3. EDA + limpeza + `cleaned_base_01.csv`.
4. STL + \(F_s\) + decisão sobre `m` sazonal (e Fourier terms se necessário).
5. Features + parquet + revisão de leakage das externas climáticas.
6. Definir `h`, origens, split treino-interno vs. teste (aproveitando a fronteira 2017-01-01 já fornecida).
7. Tuning no treino (um modelo piloto, p.ex. Elastic Net, para validar o WF).
8. Completar os 4 modelos no mesmo calendário de origens.
9. MAE, resíduos, importância, persistência completa.
10. Reexecutar o notebook do zero (Restart & Run All) a partir de `notebooks/`.

---

## 7. Critérios de aceite (esta branch)

O notebook 1 está aceito quando:

1. Roda de ponta a ponta com seed fixo e caminhos `../data/base_01` e `../artifacts/base_01`.
2. Raws intocados; limpo e previsões com nomenclatura ADR-0005.
3. Quatro modelos, mesmo WF, mesmo número de previsões OOS.
4. MAE só OOS; ranking só desta base.
5. Ljung-Box e gráficos de resíduos por modelo.
6. RF + Elastic Net com importância; scaler só no treino do fold.
7. Dicionário de disponibilidade preenchido; `humidity`/`wind_speed`/`meanpressure` contemporâneos **não** usados como feature do futuro.

---

## 8. Fora de escopo

- `notebooks/base_02.ipynb` … `base_05.ipynb`
- `notebooks/relatorio.ipynb` e seções 1–14 consolidadas
- Vitórias globais / posição média entre bases
- HTML/PDF finais, apresentação, zip do grupo
- Preencher integrantes do PRD (salvo o responsável por esta base, se o grupo pedir)
- ADR de horizonte **único** para as cinco bases (documentar aqui só o `h` **deste** notebook)

Uma linha de encadeamento: os CSVs desta pasta são a contribuição da base 1 para o `relatorio.ipynb`.

---

## 9. Referências internas

- [`PRD.md`](PRD.md) · [`SDD.md`](SDD.md) · [`RULES.md`](RULES.md) · [`AGENTS.md`](AGENTS.md)
- ADR-0001 a ADR-0005
- [`specs/spec-dados.md`](specs/spec-dados.md) · [`spec-feature-engineering.md`](specs/spec-feature-engineering.md) · [`spec-validacao.md`](specs/spec-validacao.md) · [`spec-modelos.md`](specs/spec-modelos.md) · [`spec-avaliacao.md`](specs/spec-avaliacao.md)
- [`data/README.md`](../data/README.md) · [`artifacts/README.md`](../artifacts/README.md) · [`notebooks/README.md`](../notebooks/README.md)
- [`plan_g5.md`](plan_g5.md) — plano análogo da base 5, mesmo time de especialização
- [`document-reference/grupo1/Pipeline SARIMAX.ipynb`](../document-reference/grupo1/Pipeline%20SARIMAX.ipynb) · [`document-reference/grupo1/4 - HoltWinters.ipynb`](../document-reference/grupo1/4%20-%20HoltWinters.ipynb) — referência metodológica
