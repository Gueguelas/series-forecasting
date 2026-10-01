"""Funções auxiliares compartilhadas pelo notebook base_01 (grupo1 / Elastic Net).

Vive em notebooks/ (ADR-0004 -- sem pacote src/). Importado apenas por base_01.ipynb.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import STL


# ---------------------------------------------------------------------------
# Métricas e diagnóstico
# ---------------------------------------------------------------------------

def mae(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def seasonal_strength(series: pd.Series, period: int, robust: bool = True) -> float:
    """Fs = max(0, 1 - Var(resid) / Var(seasonal + resid)) -- STL (Wang, Smith & Hyndman, 2006)."""
    stl = STL(series, period=period, robust=robust).fit()
    var_resid = stl.resid.var()
    var_seasonal_resid = (stl.seasonal + stl.resid).var()
    fs = max(0.0, 1 - var_resid / var_seasonal_resid)
    return float(fs)


def ljung_box_table(resid: pd.Series, lags=(7, 14, 30)) -> pd.DataFrame:
    resid = pd.Series(resid).dropna()
    return acorr_ljungbox(resid, lags=list(lags), return_df=True)


# ---------------------------------------------------------------------------
# Carga e limpeza
# ---------------------------------------------------------------------------

def load_raw_series(data_dir: Path) -> pd.DataFrame:
    train = pd.read_csv(data_dir / "DailyDelhiClimateTrain_grupo1.csv", parse_dates=["date"])
    test = pd.read_csv(data_dir / "DailyDelhiClimateTest_grupo1.csv", parse_dates=["date"])
    full = (
        pd.concat([train, test], ignore_index=True)
        .sort_values("date")
        .drop_duplicates(subset="date", keep="last")  # 2017-01-01 aparece nos dois arquivos com valores
        .set_index("date")                              # divergentes; ficamos com a versao do arquivo de teste.
        .asfreq("D")
    )
    return full


def clean_series(df: pd.DataFrame, pressure_bounds=(990.0, 1040.0)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica as decisoes da Secao C do plano. Retorna (df_limpo, tabela_de_decisoes)."""
    df = df.copy()
    decisions = []

    n_missing_before = df.isna().sum().sum()
    decisions.append(("Frequencia", "asfreq('D')", "Serie diaria continua (sem gaps na uniao treino+teste)"))

    lo, hi = pressure_bounds
    outliers = ~df["meanpressure"].between(lo, hi)
    n_outliers = int(outliers.sum())
    df.loc[outliers, "meanpressure"] = np.nan
    df["meanpressure"] = df["meanpressure"].interpolate(method="time").bfill().ffill()
    decisions.append((
        "Outliers meanpressure",
        f"Fora de [{lo}, {hi}] hPa -> NaN -> interpolacao temporal",
        f"{n_outliers} valores implausiveis (ex.: -3.04, 7679.33) documentados em GRUPO1.md",
    ))

    neg_wind = df["wind_speed"] < 0
    if neg_wind.any():
        df.loc[neg_wind, "wind_speed"] = np.nan
        df["wind_speed"] = df["wind_speed"].interpolate(method="time")
        decisions.append(("wind_speed negativo", "NaN -> interpolacao temporal", f"{int(neg_wind.sum())} valores"))

    bad_humidity = ~df["humidity"].between(0, 100)
    if bad_humidity.any():
        df.loc[bad_humidity, "humidity"] = df["humidity"].clip(0, 100)
        decisions.append(("humidity fora de [0,100]", "clip(0, 100)", f"{int(bad_humidity.sum())} valores"))

    n_missing_after = df.isna().sum().sum()
    decisions.append(("Missing residual", f"{n_missing_before} -> {n_missing_after}", "Interpolacao temporal cobre gaps pontuais"))

    decisions_df = pd.DataFrame(decisions, columns=["Etapa", "Decisao", "Justificativa"])
    return df, decisions_df


# ---------------------------------------------------------------------------
# Feature engineering (Secao E) -- ADR-0003 anti-leakage
# ---------------------------------------------------------------------------

TARGET = "meantemp"
EXTERNALS = ["humidity", "wind_speed", "meanpressure"]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Vetor tabular unico para Random Forest e Elastic Net.

    Todas as externas entram como lag (>=1) -- nunca o valor do dia previsto (Secao 2.2).
    """
    feat = pd.DataFrame(index=df.index)

    for lag in (1, 2, 3, 7, 14, 21, 30, 365):
        feat[f"{TARGET}_lag_{lag}"] = df[TARGET].shift(lag)

    for col in EXTERNALS:
        for lag in (1, 7, 14):
            feat[f"{col}_lag_{lag}"] = df[col].shift(lag)

    # janelas moveis fechadas no passado (shift 1 antes do rolling)
    shifted_target = df[TARGET].shift(1)
    feat[f"{TARGET}_roll_mean_7"] = shifted_target.rolling(7).mean()
    feat[f"{TARGET}_roll_std_7"] = shifted_target.rolling(7).std()
    feat[f"{TARGET}_roll_mean_30"] = shifted_target.rolling(30).mean()
    feat[f"{TARGET}_roll_std_30"] = shifted_target.rolling(30).std()

    # calendario -- known_ahead na data prevista
    doy = df.index.dayofyear
    dow = df.index.dayofweek
    feat["day_of_year"] = doy
    feat["month"] = df.index.month
    feat["day_of_week"] = dow
    feat["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    feat["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    feat["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    feat["dow_cos"] = np.cos(2 * np.pi * dow / 7)

    feat[TARGET] = df[TARGET]
    return feat


def fourier_exog(index: pd.DatetimeIndex, n_harmonics: int = 2, period: float = 365.25) -> pd.DataFrame:
    """Termos de Fourier anuais -- exogena leve para SARIMAX em vez de seasonal_order literal m=365."""
    doy = index.dayofyear.values.astype(float)
    data = {}
    for k in range(1, n_harmonics + 1):
        data[f"fourier_sin_{k}"] = np.sin(2 * np.pi * k * doy / period)
        data[f"fourier_cos_{k}"] = np.cos(2 * np.pi * k * doy / period)
    return pd.DataFrame(data, index=index)


def sarimax_exog(df: pd.DataFrame, n_harmonics: int = 2, use_lags: bool = True) -> pd.DataFrame | None:
    """Exogena do SARIMAX no treino: Fourier(known_ahead) + lag_1 das externas (lag_only).

    n_harmonics=0 desliga o Fourier; use_lags=False desliga as externas. Sem nenhuma das
    duas, devolve None (SARIMAX puramente univariado).

    A primeira linha fica com NaN nos lags (nao ha dia anterior). Ela NAO eh preenchida:
    um bfill copiaria o valor do proprio dia (contemporaneo); fit_sarimax descarta a linha.
    """
    exog = fourier_exog(df.index, n_harmonics=n_harmonics)
    if use_lags:
        for col in EXTERNALS:
            exog[f"{col}_lag1"] = df[col].shift(1)
    if exog.shape[1] == 0:
        return None
    return exog


def sarimax_future_exog(origin_row: pd.Series, forecast_dates: pd.DatetimeIndex, n_harmonics: int = 2,
                        use_lags: bool = True) -> pd.DataFrame | None:
    """Exogena para os h passos futuros do SARIMAX.

    Fourier eh determinista (known_ahead) e varia por data. As externas (lag_only) sao
    CONGELADAS no ultimo valor conhecido em origin_date -- nao existe leitura real de
    humidity/wind_speed/meanpressure para datas apos a origem, entao repetir o ultimo
    valor observado eh a unica opcao sem vazamento (nao ha modelo de previsao dessas
    externas neste notebook).
    """
    exog = fourier_exog(forecast_dates, n_harmonics=n_harmonics)
    if use_lags:
        for col in EXTERNALS:
            exog[f"{col}_lag1"] = origin_row[col]
    if exog.shape[1] == 0:
        return None
    return exog


def fit_sarimax(train_df: pd.DataFrame, params: dict, maxiter: int = 100):
    """Ajusta o SARIMAX de um candidato do grid e devolve o resultado do statsmodels.

    params: order=(p,d,q), seasonal_order=(P,D,Q,m) para m curto (7 ou 30), fourier_k
    (harmonicos anuais; 0 = sem Fourier), annual_diff (D=1 com m=365) e exog_lags (lag-1
    das externas). A diferenciacao anual eh feita manualmente (y_t - y_{t-365}, idem para
    as exogenas) e o modelo roda sobre a serie diferenciada: um seasonal_order literal com
    m=365 cria ~366 estados no filtro de Kalman (inviavel, ver Secao F do notebook).
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    y = train_df[TARGET]
    exog = sarimax_exog(train_df, n_harmonics=params.get("fourier_k", 0), use_lags=params.get("exog_lags", True))
    if params.get("annual_diff", False):
        y = y.diff(365)
        exog = None if exog is None else exog.diff(365)
    # descarta as linhas iniciais sem lag/diferenca disponivel (mesma politica do dropna tabular)
    valid = y.notna() if exog is None else y.notna() & exog.notna().all(axis=1)
    y, exog = y[valid], (None if exog is None else exog[valid])
    return SARIMAX(y, exog=exog, order=params["order"], seasonal_order=params.get("seasonal_order", (0, 0, 0, 0)),
                   enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=maxiter)


def forecast_sarimax(res, train_df: pd.DataFrame, params: dict, horizon: int) -> np.ndarray:
    """Previsao h passos do resultado de fit_sarimax, na escala original de meantemp."""
    k, lags = params.get("fourier_k", 0), params.get("exog_lags", True)
    annual_diff = params.get("annual_diff", False)
    origin_date = train_df.index.max()
    forecast_dates = pd.date_range(origin_date + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_exog = sarimax_future_exog(train_df.iloc[-1], forecast_dates, n_harmonics=k, use_lags=lags)
    if annual_diff and future_exog is not None:
        # exogena diferenciada: valor futuro menos o valor observado 365 dias antes (ja conhecido)
        past = sarimax_exog(train_df, n_harmonics=k, use_lags=lags).reindex(forecast_dates - pd.Timedelta(days=365))
        future_exog = future_exog - past.to_numpy()
    pred = res.get_forecast(horizon, exog=future_exog).predicted_mean.to_numpy()
    if annual_diff:
        # desfaz a diferenca sazonal: y_{t+k} = z_{t+k} + y_{t+k-365} (k <= 7, sempre observado)
        pred = pred + train_df[TARGET].reindex(forecast_dates - pd.Timedelta(days=365)).to_numpy()
    return pred


def recursive_tabular_forecast(model, feature_cols: list[str], history_df: pd.DataFrame, horizon: int) -> np.ndarray:
    """Previsao recursiva multi-step para modelos tabulares (Random Forest, Elastic Net).

    As lags do alvo sao realimentadas com a propria previsao (recursivo, padrao para
    forecasting tabular). As externas (lag_only) sao CONGELADAS no ultimo valor
    conhecido em origin_date -- ver docstring de sarimax_future_exog para a justificativa.
    """
    origin_date = history_df.index.max()
    future_dates = pd.date_range(origin_date + pd.Timedelta(days=1), periods=horizon, freq="D")

    extended = history_df.copy()
    future_rows = pd.DataFrame(index=future_dates, columns=history_df.columns, dtype=float)
    for col in EXTERNALS:
        future_rows[col] = history_df[col].iloc[-1]
    extended = pd.concat([extended, future_rows])

    preds = []
    for date in future_dates:
        feat_all = build_features(extended.loc[:date])
        x = feat_all.loc[[date], feature_cols]
        y_hat = float(model.predict(x)[0])
        extended.loc[date, TARGET] = y_hat
        preds.append(y_hat)
    return np.array(preds)


# ---------------------------------------------------------------------------
# Walk-forward (Secao F / spec-validacao.md)
# ---------------------------------------------------------------------------

@dataclass
class WalkForwardConfig:
    horizon: int = 7
    origin_step: int = 7
    first_origin: pd.Timestamp = None
    last_origin: pd.Timestamp = None


def build_origins(cfg: WalkForwardConfig) -> list[pd.Timestamp]:
    origins = []
    current = cfg.first_origin
    while current <= cfg.last_origin:
        origins.append(current)
        current = current + pd.Timedelta(days=cfg.origin_step)
    return origins


def tune_single_shot(candidates: list[dict], fit_predict_fn, subtrain: pd.DataFrame, validation: pd.DataFrame) -> pd.DataFrame:
    """Tuning barato (1 fit por candidato): ajusta no subtreino, preve toda a validacao
    de uma vez (sem walk-forward), escolhe por MAE -- mesmo espirito do notebook de
    referencia SARIMAX (Secao 6-8: MAE na validacao interna, teste final intocado)."""
    rows = []
    y_val = validation[TARGET].to_numpy()
    for params in candidates:
        row = dict(params)
        try:
            preds = fit_predict_fn(subtrain, len(validation), params)
            row["mae_validacao"] = mae(y_val, preds)
            row["status"] = "ok"
        except Exception as exc:  # noqa: BLE001 -- registrar qualquer falha de convergencia
            row["mae_validacao"] = np.nan
            row["status"] = f"falha: {type(exc).__name__}: {exc}"
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mae_validacao", na_position="last").reset_index(drop=True)


def tune_by_walkforward(candidates: list[dict], forecaster_factory, df: pd.DataFrame, cfg: WalkForwardConfig,
                        ic_fn=None, n_jobs: int = 1) -> pd.DataFrame:
    """Tuning fiel ao protocolo de producao: roda walk-forward (mesmo h desta base) sobre
    as origens de VALIDACAO para cada candidato e ranqueia pelo MAE agregado. Mais caro que
    tune_single_shot, mas evita o vies de tunar num horizonte diferente do usado no teste.

    ic_fn(params) -> dict opcional (ex.: {"aic": ..., "bic": ...}) calculado num ajuste unico
    com dados ate a primeira origem de validacao -- criterio complementar ao MAE.
    A coluna `candidato` guarda a posicao em `candidates`: use candidates[int(...)] para
    recuperar os parametros originais (o DataFrame converte None em NaN).

    n_jobs paraleliza as tarefas independentes (candidato x origem, mais o ajuste de AIC/BIC)
    em processos separados; o resultado eh identico ao sequencial. `segundos` soma o tempo de
    todas as tarefas do candidato (custo total, nao tempo de parede).
    """
    origins = build_origins(cfg)
    tasks = [("wf", i, origin) for i in range(len(candidates)) for origin in origins]
    if ic_fn is not None:
        tasks += [("ic", i, None) for i in range(len(candidates))]

    def _run(kind, i, origin):
        t0 = time.time()
        try:
            if kind == "wf":
                out = _forecast_origin(forecaster_factory(candidates[i]), df, origin, cfg.horizon, "tuning")
            else:
                out = ic_fn(candidates[i])
            return kind, i, out, None, time.time() - t0
        except Exception as exc:  # noqa: BLE001 -- registrar qualquer falha de convergencia
            return kind, i, None, f"falha: {type(exc).__name__}: {exc}", time.time() - t0

    outputs = _parallel(_run, tasks, n_jobs)

    rows = []
    for i, params in enumerate(candidates):
        mine = [o for o in outputs if o[1] == i]
        errors = [o[3] for o in mine if o[3] is not None]
        row = {"candidato": i, **params}
        if errors:
            row["mae_validacao"] = np.nan
            row["status"] = errors[0]
        else:
            preds = pd.DataFrame([r for o in mine if o[0] == "wf" for r in o[2]])
            row["mae_validacao"] = mae(preds["y_true"], preds["y_pred"])
            for o in mine:
                if o[0] == "ic":
                    row.update(o[2])
            row["status"] = "ok"
        row["segundos"] = round(sum(o[4] for o in mine), 1)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mae_validacao", na_position="last").reset_index(drop=True)


def _parallel(fn, tasks: list[tuple], n_jobs: int) -> list:
    """Executa fn(*task) para cada task, em paralelo quando n_jobs != 1 (joblib/loky)."""
    if n_jobs == 1:
        return [fn(*t) for t in tasks]
    import os
    from joblib import Parallel, delayed

    # os workers sao processos novos: garantir que achem ts_common (vive em notebooks/)
    here = str(Path(__file__).resolve().parent)
    paths = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    if here not in paths:
        os.environ["PYTHONPATH"] = os.pathsep.join([here] + [p for p in paths if p])
    return Parallel(n_jobs=n_jobs)(delayed(_quiet)(fn, *t) for t in tasks)


def _quiet(fn, *args):
    """Roda fn no worker sem os ConvergenceWarning do statsmodels (o worker nao herda o
    warnings.filterwarnings do notebook; falhas reais continuam no status do candidato)."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return fn(*args)


def _forecast_origin(forecaster_fn, df: pd.DataFrame, origin_date: pd.Timestamp, horizon: int, model_name: str) -> list[dict]:
    """Uma origem do walk-forward: treina so com dados <= origin_date e preve os h dias seguintes."""
    train_df = df.loc[:origin_date]
    forecast_dates = pd.date_range(origin_date + pd.Timedelta(days=1), periods=horizon, freq="D")
    y_true = df.loc[forecast_dates, TARGET].to_numpy()

    t0 = time.time()
    y_pred = forecaster_fn(train_df, horizon)
    elapsed = time.time() - t0

    return [
        {
            "origin_date": origin_date,
            "forecast_date": fdate,
            "y_true": yt,
            "y_pred": yp,
            "horizon_step": step,
            "model": model_name,
            "fit_seconds": elapsed,
        }
        for step, (fdate, yt, yp) in enumerate(zip(forecast_dates, y_true, y_pred), start=1)
    ]


def run_walk_forward(forecaster_fn, df: pd.DataFrame, cfg: WalkForwardConfig, model_name: str,
                     n_jobs: int = 1) -> pd.DataFrame:
    """forecaster_fn(train_df, horizon) -> np.ndarray de tamanho horizon (na escala original).

    As origens sao independentes (cada uma so ve dados <= origin_date), entao n_jobs != 1
    as distribui entre processos sem mudar o resultado.
    """
    tasks = [(forecaster_fn, df, origin, cfg.horizon, model_name) for origin in build_origins(cfg)]
    outputs = _parallel(_forecast_origin, tasks, n_jobs)
    return pd.DataFrame([row for rows in outputs for row in rows])


# ---------------------------------------------------------------------------
# Persistencia (ADR-0005)
# ---------------------------------------------------------------------------

def save_predictions(preds: pd.DataFrame, data_dir: Path, base_id: str, model_slug: str) -> Path:
    # fit_seconds: tempo de ajuste + previsao daquela origem (§5.6), repetido nos h passos
    out = preds[["origin_date", "forecast_date", "y_true", "y_pred", "horizon_step", "fit_seconds"]].copy()
    path = data_dir / f"predictions_{model_slug}_{base_id}.csv"
    out.to_csv(path, index=False)
    return path


def save_residuals(preds: pd.DataFrame, data_dir: Path, base_id: str, model_slug: str) -> Path:
    out = preds.copy()
    out["residual"] = out["y_true"] - out["y_pred"]
    path = data_dir / f"residuals_{model_slug}_{base_id}.csv"
    out[["origin_date", "forecast_date", "horizon_step", "residual"]].to_csv(path, index=False)
    return path


def save_meta(artifact_dir: Path, base_id: str, model_slug: str, hyperparams: dict, random_state: int, extra: dict | None = None) -> Path:
    import sklearn
    import statsmodels
    from datetime import datetime, timezone

    meta = {
        "base_id": base_id,
        "model": model_slug,
        "hyperparams": hyperparams,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "random_state": random_state,
        "library_versions": {
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "sklearn": sklearn.__version__,
            "statsmodels": statsmodels.__version__,
        },
    }
    if extra:
        meta.update(extra)
    path = artifact_dir / f"{model_slug}_meta.json"
    path.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")
    return path
