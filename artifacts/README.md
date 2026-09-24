# Artifacts — modelos treinados

Pasta para **modelos serializados** (pickles) gerados durante o treinamento nos notebooks.

Está no **`.gitignore`** (exceto este README). Cada integrante regenera localmente; incluir no zip Odete se o enunciado exigir reprodução sem re-treinar.

## Estrutura

```
artifacts/
├── base_01/
│   ├── sarimax.pkl
│   ├── sarimax_meta.json
│   ├── holt_winters.pkl
│   ├── holt_winters_meta.json
│   ├── random_forest.pkl
│   ├── random_forest_meta.json
│   ├── elastic_net.pkl          # modelo de especialização do grupo 3
│   └── elastic_net_meta.json
├── base_02/
│   └── ...
└── ...
```

## Nomenclatura de arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `{modelo}.pkl` | Objeto do modelo treinado (`joblib` ou `pickle`) |
| `{modelo}_meta.json` | Hiperparâmetros finais, `base_id`, data/hora, seed, versões de libs |

### Slugs de modelo (`{modelo}`)

| Modelo | Slug do arquivo |
|--------|-----------------|
| SARIMAX | `sarimax` |
| Holt-Winters | `holt_winters` |
| Random Forest | `random_forest` |
| Especialização (Grupo 3) | `elastic_net` |

> Se o grupo mudar de especialização, usar slug em `snake_case` do algoritmo (ex.: `xgboost`, `svr`, `mlp`, `pls`).

## Exemplo de salvamento

```python
import json
import joblib
from pathlib import Path
from datetime import datetime, timezone

BASE_ID = "base_01"
MODEL_SLUG = "random_forest"
ARTIFACT_DIR = Path("../artifacts") / BASE_ID
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(model, ARTIFACT_DIR / f"{MODEL_SLUG}.pkl")

meta = {
    "base_id": BASE_ID,
    "model": MODEL_SLUG,
    "hyperparams": model.get_params(),
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "random_state": 42,
}
(ARTIFACT_DIR / f"{MODEL_SLUG}_meta.json").write_text(
    json.dumps(meta, indent=2, default=str)
)
```

## Exemplo de carregamento

```python
model = joblib.load(Path("../artifacts") / BASE_ID / "random_forest.pkl")
```

## Regras

- Um diretório por base (`artifacts/base_XX/`), espelhando `data/base_XX/`.
- Salvar **após** seleção final de hiperparâmetros (modelo pronto para walk-forward ou modelo final).
- Preferir `joblib` para modelos scikit-learn; `pickle` para objetos statsmodels quando necessário.
- Não commitar pickles no git — apenas documentar no notebook que o caminho é `../artifacts/`.
