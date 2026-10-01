# Grupo 1 — Daily Climate Time Series (Delhi)

## Fonte

- Kaggle: [Daily Climate time series data](https://www.kaggle.com/datasets/sumanthvrao/daily-climate-time-series-data)
- Autor: sumanthvrao
- Licença: CC0-1.0 (domínio público)

## Descrição

Série temporal diária com variáveis climáticas da cidade de Delhi, Índia, coletadas entre 2013 e 2017. O dataset já vem dividido em conjuntos de treino e teste pelo autor original.

## Arquivos

| Arquivo | Período | Linhas (com header) |
|---|---|---|
| `DailyDelhiClimateTrain_grupo1.csv` | 2013-01-01 a 2016-12-31 | 1463 |
| `DailyDelhiClimateTest_grupo1.csv` | 2017-01-01 a 2017-04-24 | 115 |

## Colunas

| Coluna | Descrição | Unidade |
|---|---|---|
| `date` | Data da observação | `YYYY-MM-DD` |
| `meantemp` | Temperatura média diária | °C |
| `humidity` | Umidade relativa média diária | % |
| `wind_speed` | Velocidade média do vento | km/h |
| `meanpressure` | Pressão atmosférica média | atm (alguns valores parecem estar em hPa/mbar — atenção a outliers, ex. valores como `59.0` no primeiro registro do teste) |

## Como foi obtido

```bash
kaggle datasets download -d sumanthvrao/daily-climate-time-series-data --unzip -p data/
```

Os arquivos originais (`DailyDelhiClimateTrain.csv`, `DailyDelhiClimateTest.csv`) foram renomeados com o sufixo `_grupo1` para identificar a base usada pelo Grupo 1.

## Observações para preparação/ingestão

- `meanpressure` apresenta outliers evidentes (ex.: valores próximos de 1000+ misturados com valores baixos como `59.0`) — validar e tratar antes de usar em modelos.
- A série de treino cobre 4 anos completos; a de teste cobre apenas os primeiros ~4 meses de 2017.
- `date` deve ser convertida para tipo datetime e usada como índice temporal para forecasting.
