# Plano operacional — Notebook 5 (`base_05`)

**Status:** Vigente para a branch `grupo-5`  
**Responsável desta base:** integrante da branch `grupo-5`  
**Grupo do trabalho:** 3 — especialização **Elastic Net** (não confundir com o Grupo 5 do enunciado, que usa PLS)  
**Notebook:** [`notebooks/base_05.ipynb`](../notebooks/base_05.ipynb) (a criar na implementação)  
**Dados:** Microsoft Stock → pasta [`data/base_05/`](../data/README.md)  
**Enunciado:** [`docs/instrucoes.pdf`](../docs/instrucoes.pdf)  
**Specs aplicáveis:** dados, features, validação, modelos, avaliação — só o recorte desta base

Este documento é a receita para **uma** das cinco bases. Cada integrante implementa o pipeline completo na sua base. Os artefatos em `data/base_05/` alimentam depois o `relatorio.ipynb` do grupo; **este plano não cobre** as bases 1–4, o relatório consolidado, a apresentação oral nem o zip Odete.

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

| Etapa do PDF | O que fazer em `base_05.ipynb` |
|--------------|--------------------------------|
| §5.1 | Documentar, explorar, limpar a série MSFT |
| §5.2 | STL do alvo + força da sazonalidade |
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
- **ADR-0005:** CSVs/parquet/JSON em `data/base_05/`; pickles em `artifacts/base_05/`.

### Proibições

- Commit ou push sem pedido explícito  
- Usar o período de teste final para escolher hiperparâmetros  
- Holt-Winters com variáveis externas  
- `Open`/`High`/`Low`/`Volume` **do mesmo pregão** que o `Close` a prever (vazamento)  
- Interpolar sábado/domingo como se houvesse pregão  
- Alterar o arquivo raw  

Código e nomes de variáveis em **inglês**. Narrativa do notebook em **português**. `random_state = 42` salvo decisão documentada.

---

## 1. Identidade, pastas e célula 0

| Item | Valor |
|------|--------|
| `BASE_ID` | `"base_05"` |
| Raw (nome original, não renomear) | `data/base_05/Microsoft_Stock.csv` |
| Situação atual | o CSV ainda está em `data/Microsoft_Stock.csv` (raiz) — **primeiro passo da implementação** é colocá-lo em `data/base_05/` e **não** deixar cópia na raiz (na raiz de `data/` só `README.md` e, no futuro, consolidados do grupo) |
| Notebook | `notebooks/base_05.ipynb` |
| Working directory | pasta `notebooks/` (padrão do Jupyter ao abrir o arquivo dali) |

Célula 0 (obrigatória):

```python
from pathlib import Path
import numpy as np
import pandas as pd

BASE_ID = "base_05"
RANDOM_STATE = 42
DATA_DIR = Path("../data") / BASE_ID
ARTIFACT_DIR = Path("../artifacts") / BASE_ID
RAW_FILE = DATA_DIR / "Microsoft_Stock.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(RANDOM_STATE)
```

Funções auxiliares (MAE, walk-forward, scaler por fold, persistência, Ljung-Box, força da sazonalidade) podem viver **no próprio notebook** ou, se o grupo criar, em `notebooks/ts_common.py` importado daqui. Não criar `src/`.

### Bibliotecas previstas

Python 3.11+ (SDD). Uso neste notebook: `pandas`, `numpy`, `matplotlib`, `seaborn`, `statsmodels` (STL, SARIMAX, Ljung-Box, ACF), `scikit-learn` (Random Forest, Elastic Net, `StandardScaler`, permutation importance), `joblib`, `pyarrow` (parquet). `pmdarima` só se auto_arima for usado e justificado. Pinagem de versões: quando o repo tiver `requirements.txt`.

---

## 2. Definição da série (documentar no início do notebook)

### 2.1 Inventário

| Campo | Valor proposto |
|-------|----------------|
| Nome | Microsoft Stock (MSFT) |
| Arquivo | `Microsoft_Stock.csv` |
| Colunas | `Date`, `Open`, `High`, `Low`, `Close`, `Volume` |
| Linhas (raw) | ~1511 (arquivo com cabeçalho + ~1511 observações) |
| Período | 2015-04-01 16:00:00 → 2021-03-31 16:00:00 (a confirmar no parse) |
| Frequência | **Pregões** (dias úteis de bolsa EUA; buracos em fins de semana e feriados) |
| Unidade do alvo | Preço de fechamento (USD) |
| Alvo | `Close` |
| Externas | `Open`, `High`, `Low`, `Volume` (≥2, requisito do PDF §4) |

Fonte a citar no notebook (completar com a origem real do CSV: Kaggle, Yahoo, material da disciplina, etc.).

### 2.2 Dicionário e disponibilidade (ADR-0003)

Hipótese de previsão: na origem `t` (fim do pregão `t` ou último `Close` conhecido), prever o `Close` dos **próximos `h` pregões**.

| Coluna | Papel | Disponibilidade | Tratamento |
|--------|--------|-----------------|------------|
| `Date` | Índice | `known_ahead` | Datetime do pregão |
| `Close` | Alvo | — | Lags e janelas só até `t` |
| `Open`, `High`, `Low`, `Volume` | Externas | `lag_only` | Nunca o valor do dia `t+k` (`k≥1`) nem OHLC do mesmo dia se o alvo for o `Close` **desse** dia em setup contemporâneo. Para horizonte futuro, usar apenas valores ≤ `t` |
| Dia da semana, mês, fim de mês | Calendário | `known_ahead` | Valor da **data prevista** |
| Feriado de bolsa EUA | Calendário | `known_ahead` | Se usado, documentar calendário (NYSE) |

**Vazamento clássico a recusar:** usar `Open`/`High`/`Low`/`Volume` do dia `t+1` para “prever” `Close` de `t+1` (informação do mesmo pregão, em grande parte simultânea ou posterior ao fechamento).

### 2.3 Horizonte e walk-forward (desta base)

O `h` **global das cinco bases** é decisão do grupo (futura ADR-0006 no repo; o número 0005 já é persistência). **Neste notebook**, escolher e **documentar** um `h` em **pregões**, não em dias corridos.

| Parâmetro | Proposta inicial | Como fechar |
|-----------|------------------|-------------|
| `horizon` (`h`) | `1` (um pregão à frente) **ou** `5` (semana de pregões) | Justificar no markdown; usar o mesmo `h` nos 4 modelos |
| `origin_step` | 1 pregão | Avançar a origem de pregão em pregão (ou a cada `h` se o grupo quiser origens não sobrepostas — documentar) |
| `train_min_obs` | p.ex. 252 pregões (~1 ano) | Ajustar após EDA se a série for curta demais para STL/`m` |
| Período de teste | último bloco temporal (p.ex. últimos 20% dos pregões, ou último ano) | **Congelar antes do tuning**; não olhar MAE de teste para escolher HP |

Todos os modelos desta base: **mesmo** `h`, mesmas `origin_date`, mesmo conjunto de pares `(origin, forecast_date)`.

**Aceite de conformidade:** os quatro CSVs `predictions_*_base_05.csv` têm o **mesmo número de linhas** e o mesmo conjunto de `(origin_date, forecast_date, horizon_step)`.

---

## 3. Estrutura do notebook (checklist de aceite)

Espelhar [`specs/spec-relatorio.md`](specs/spec-relatorio.md) §2 e [`notebooks/README.md`](../notebooks/README.md).

### Seção A — Setup

- [ ] Célula 0 (caminhos, seed, versões impressas: pandas, sklearn, statsmodels)
- [ ] Conferir `RAW_FILE.exists()`

### Seção B — Documentação e EDA (§5.1)

- [ ] Texto: fonte, descrição, período, frequência, unidade, significado de cada coluna  
- [ ] Tabela-dicionário com coluna `availability`  
- [ ] Gráfico da série `Close`  
- [ ] Gráficos de `Open`, `High`, `Low`, `Volume` (ou um painel OHLC + volume)  
- [ ] Contagem e padrão temporal de missing  
- [ ] Duplicidade de timestamp  
- [ ] Irregularidades: gaps > 1 pregão esperado (feriados vs falhas)  
- [ ] Outliers: método documentado (p.ex. retorno diário vs IQR / z-score robusto) — **não** remover saltos de mercado sem justificativa  

### Seção C — Limpeza

Tabela markdown obrigatória:

| Etapa | Decisão | Justificativa |
|-------|---------|---------------|
| Parse de `Date` | `pd.to_datetime`; ordenar; índice | |
| Timezone / hora 16:00 | Tratar como data de pregão (normalizar para date) | Hora do close não é frequência intradaily |
| Frequência | Índice de pregões (`B` ou calendário custom, **sem** preencher fds com interpolação do preço) | PDF §4: regularizar sem inventar pregões |
| Missing | | |
| Outliers | | |
| Transformação do alvo | Nível em USD **ou** log; se log, MAE do relatório deve deixar claro se é no nível original (preferir **desfazer** transformação antes do MAE) | Comparação justa |

- [ ] Salvar `data/base_05/cleaned_base_05.csv` **sem** alterar o raw  

### Seção D — STL e sazonalidade (§5.2)

- [ ] STL de `Close` (nível usado na modelagem, ou documentar se STL é no log)  
- [ ] Período sazonal `m`: proposta **5** (semana de pregões). Se a força for ~0, manter `m=5` no HW/SARIMAX como tentativa e discutir  
- [ ] Interpretar tendência (alta 2015–2021, quebras, COVID-19 em 2020)  
- [ ] Interpretar sazonalidade e residual  
- [ ] Força da sazonalidade (método da disciplina):

\[
F_s = \max\left(0,\ 1 - \frac{\mathrm{Var}(R)}{\mathrm{Var}(S+R)}\right)
\]

onde `S` e `R` vêm do STL.

### Seção E — Feature engineering (§5.3, ADR-0003)

Conjunto **tabular único** para Random Forest e Elastic Net. Exemplos mínimos:

| Categoria | Exemplos | Regra |
|-----------|----------|--------|
| Lags do alvo | `close_lag_1`, `close_lag_5` | Só passado relativo à origem |
| Lags de externas | `volume_lag_1`, `high_lag_1`, … | `lag_only` |
| Janelas | média e desvio de retornos ou de `Close` em 5 e 21 pregões | Janela **fechada no passado** (shift 1 antes do rolling, se o rolling incluir `t`) |
| Calendário | `dow`, `month`, `is_month_end` | `known_ahead` na data **prevista** |
| Cíclico | `sin/cos` do dia da semana (`period=5`) e do dia do ano | |

NaNs do início da série: **drop** das primeiras linhas no treino (preferencial). Forward-fill só com justificativa e sem olhar o futuro.

- [ ] Lista markdown das features finais e parâmetros (lags, janelas)  
- [ ] Checklist anti-leakage da spec de features  
- [ ] `data/base_05/features_base_05.parquet`  

**SARIMAX:** exógenas alinhadas à disponibilidade (lags de volume/OHLC ou calendário). Não é obrigatório o mesmo vetor tabular.  
**Holt-Winters:** somente `Close`.

**Scaler:** `StandardScaler` (e qualquer normalização) com `fit` **apenas** no treino de cada origem do walk-forward. Elastic Net **exige** padronização.

### Seção F — Hiperparâmetros (§5.5) e walk-forward (§5.4–5.6)

Espaço mínimo a investigar (documentar grid/random, ranges, procedimento **no treino**, valores finais, justificativa):

| Modelo | Slug | Investigar |
|--------|------|------------|
| SARIMAX | `sarimax` | `(p,d,q)`, `(P,D,Q)`, `m`, AIC/BIC, quais exógenas |
| Holt-Winters | `holt_winters` | trend, seasonal, damped, `m`, suavização |
| Random Forest | `random_forest` | `n_estimators`, `max_depth`, `min_samples_split`, `min_samples_leaf`, `max_features` |
| Elastic Net | `elastic_net` | `alpha`, `l1_ratio` + pipeline com scaler |

Loop walk-forward:

```
Para cada origin_date nas origens de teste:
    train = observações com timestamp <= origin_date
    ajustar modelo com HP já escolhidos (fixos)
    y_hat = previsão dos próximos h pregões
    registrar origin_date, forecast_date, y_true, y_pred, horizon_step, tempo
```

- [ ] Mesmas origens para os 4 modelos  
- [ ] Sem acesso a dados após `origin_date` em treino/features  
- [ ] Registrar tempo de execução por combinação  

### Seção G — MAE e ranking (§6, só esta base)

```python
mae = np.mean(np.abs(y_true - y_pred))
```

- [ ] MAE sobre **todas** as previsões OOS de cada modelo  
- [ ] Tabela dos 4 MAEs + ranking (1º = menor MAE)  
- [ ] Discutir por que o vencedor faz sentido nesta série (tendência forte, ruído, sazonalidade fraca, etc.)  
- [ ] `data/base_05/mae_base_05.csv`  

Não calcular “MAE médio das cinco bases” aqui.

### Seção H — Resíduos (§7)

Para cada modelo: `e = y_true - y_pred` (OOS).

- [ ] Série temporal dos resíduos  
- [ ] ACF  
- [ ] Ljung-Box + p-valor interpretado  
- [ ] Texto: viés, padrões, variabilidade, autocorrelação  
- [ ] `residuals_{modelo}_base_05.csv`  
- [ ] `ljung_box_base_05.csv`  

### Seção I — Importância (§8)

| Modelo | Método neste notebook |
|--------|------------------------|
| SARIMAX | Coeficientes, sinal, magnitude, significância |
| Holt-Winters | Nível, tendência, sazonalidade (sem FI) |
| Random Forest | Importância nativa **e/ou** permutation |
| Elastic Net | Coeficientes **após** padronização; destacar o que foi zerado (`l1_ratio`) |

Retomar no texto se as externas (lags de volume/OHLC) realmente ajudam e se estavam disponíveis na origem.

---

## 4. Persistência (ADR-0005) — só `base_05`

### 4.1 Dados (`data/base_05/`)

| Arquivo | Conteúdo |
|---------|----------|
| `Microsoft_Stock.csv` | Raw, nome original |
| `cleaned_base_05.csv` | Série limpa |
| `features_base_05.parquet` | Matriz de features |
| `predictions_{modelo}_base_05.csv` | OOS; colunas mínimas: `origin_date`, `forecast_date`, `y_true`, `y_pred`, `horizon_step` |
| `residuals_{modelo}_base_05.csv` | Resíduos OOS |
| `mae_base_05.csv` | MAE dos 4 modelos |
| `ljung_box_base_05.csv` | Teste por modelo |
| `hyperparams_{modelo}_base_05.json` | Espaço de busca + valores finais |

`{modelo}` ∈ `sarimax` | `holt_winters` | `random_forest` | `elastic_net`

**Não** é obrigação deste notebook gerar `data/mae_consolidated.csv` (relatório do grupo).

### 4.2 Modelos (`artifacts/base_05/`)

Após HP finais, para cada slug:

- `{modelo}.pkl` — `joblib` para sklearn; `pickle` para statsmodels se necessário  
- `{modelo}_meta.json` — `base_id`, `model`, `hyperparams`, `trained_at` (UTC), `random_state`, versões de libs  

Exemplo de nomes: `artifacts/base_05/elastic_net.pkl`, `artifacts/base_05/elastic_net_meta.json`.

---

## 5. Elastic Net nesta base (estudo local)

O relatório do grupo aprofundará o algoritmo (PDF §9). Neste notebook, o mínimo para não entregar “só `.fit()`”:

1. Intuição: mistura L1/L2; `l1_ratio=1` ≈ Lasso, `l1_ratio=0` ≈ Ridge.  
2. Por que padronizar (coeficientes comparáveis; `alpha` não-invariante à escala).  
3. HP escolhidos e efeito observado (esparsidade vs shrinkage).  
4. Comparar MAE com RF **na mesma matriz de features**.  
5. Interpretar coeficientes padronizados à luz de `lag_only`.

---

## 6. Ordem de implementação

1. Mover `data/Microsoft_Stock.csv` → `data/base_05/Microsoft_Stock.csv`; criar `artifacts/base_05/`.  
2. Criar `notebooks/base_05.ipynb` com célula 0 e seções A–I.  
3. EDA + limpeza + `cleaned_base_05.csv`.  
4. STL + \(F_s\).  
5. Features + parquet + revisão de leakage OHLC.  
6. Definir `h`, origens, split treino-interno vs teste.  
7. Tuning no treino (um modelo piloto, p.ex. Elastic Net, para validar o WF).  
8. Completar os 4 modelos no mesmo calendário de origens.  
9. MAE, resíduos, importance, persistência completa.  
10. Reexecutar o notebook do zero (Restart & Run All) a partir de `notebooks/`.

---

## 7. Critérios de aceite (esta branch)

O notebook 5 está aceito quando:

1. Roda de ponta a ponta com seed fixo e caminhos `../data/base_05` e `../artifacts/base_05`.  
2. Raw intocado; limpo e previsões com nomenclatura ADR-0005.  
3. Quatro modelos, mesmo WF, mesmo número de previsões OOS.  
4. MAE só OOS; ranking só desta base.  
5. Ljung-Box e gráficos de resíduos por modelo.  
6. RF + Elastic Net com importância; scaler só no treino do fold.  
7. Dicionário de disponibilidade preenchido; OHLC/volume contemporâneos **não** usados como feature do futuro.  

---

## 8. Fora de escopo

- `notebooks/base_01.ipynb` … `base_04.ipynb`  
- `notebooks/relatorio.ipynb` e seções 1–14 consolidadas  
- Vitórias globais / posição média entre bases  
- HTML/PDF finais, apresentação, zip `Grupo_03_Trabalho_Series_Temporais.zip`  
- Preencher integrantes do PRD (salvo o responsável por esta base, se o grupo pedir)  
- ADR de horizonte **único** para as cinco bases (coordenar com o grupo se o professor exigir o mesmo `h` em todas; até lá, documentar o `h` **deste** notebook)  

Uma linha de encadeamento: os CSVs desta pasta são a contribuição da base 5 para o `relatorio.ipynb`.

---

## 9. Referências internas

- [`PRD.md`](PRD.md) · [`SDD.md`](SDD.md) · [`RULES.md`](RULES.md) · [`AGENTS.md`](AGENTS.md)  
- ADR-0001 a ADR-0005  
- [`specs/spec-dados.md`](specs/spec-dados.md) · [`spec-feature-engineering.md`](specs/spec-feature-engineering.md) · [`spec-validacao.md`](specs/spec-validacao.md) · [`spec-modelos.md`](specs/spec-modelos.md) · [`spec-avaliacao.md`](specs/spec-avaliacao.md)  
- [`data/README.md`](../data/README.md) · [`artifacts/README.md`](../artifacts/README.md) · [`notebooks/README.md`](../notebooks/README.md)  
