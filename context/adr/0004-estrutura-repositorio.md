# ADR-0004: Estrutura do repositório (notebooks + dados locais)

**Status:** Aceita  
**Data:** 2026-09-10  
**Atualizado:** 2026-09-10  
**Relacionado:** [`SDD.md`](../SDD.md)

## Contexto

O projeto exige código organizado, relatório reprodutível e colaboração entre integrantes. As **entregas são notebooks** (não pacote `src/`). Os **dados são fornecidos ao grupo** e ficam na pasta `data/`, que está no `.gitignore` — cada integrante mantém a cópia local organizada da mesma forma.

## Decisão

Adotar layout centrado em notebooks:

```
series-forecasting/
├── context/              # PRD, SDD, ADRs, SPECs, RULES, AGENTS, HANDOFF
├── docs/
│   └── instrucoes.pdf
├── data/                 # GITIGNORE — raw + dados derivados (local)
│   ├── README.md         # Nomenclatura: cleaned_{base_id}.csv, etc.
│   ├── base_01/ … base_05/
│   └── mae_consolidated.csv
├── artifacts/            # GITIGNORE — modelos .pkl treinados
│   ├── README.md
│   └── base_01/ … base_05/
└── notebooks/            # TODAS as entregas de análise
    ├── README.md
    ├── base_01.ipynb     # Um notebook por dataset
    ├── base_02.ipynb
    ├── base_03.ipynb
    ├── base_04.ipynb
    ├── base_05.ipynb
    └── relatorio.ipynb   # Relatório final HTML/PDF (fonte)
```

### Regras

1. **Um notebook por dataset** em `notebooks/`, cobrindo EDA, STL, features, 4 modelos, walk-forward, MAE, resíduos e feature importance daquela base.
2. **Um diretório por dataset** em `data/`, com arquivos fornecidos + derivados (`cleaned_{base_id}.csv`, previsões, métricas).
3. **Modelos treinados** salvos em `artifacts/{base_id}/{modelo}.pkl` (ver ADR-0005).
4. Notebooks usam caminhos relativos: `../data/base_XX/` e `../artifacts/base_XX/`.
5. Pastas `data/` e `artifacts/` **não são commitadas** (exceto READMEs).
6. Não usar `src/` — lógica reprodutível vive nos notebooks versionados.

## Alternativas consideradas

| Alternativa | Contras |
|-------------|---------|
| Pacote `src/` modular | Não alinha com formato de entrega acadêmica em notebooks |
| Um único notebook monolítico | Difícil dividir trabalho entre integrantes e revisar 20 combinações |
| Dados versionados no git | Arquivos grandes; enunciado prevê bases congeladas entregues separadamente |

## Consequências

- Integrantes devem clonar o repo e **popular `data/` localmente** com os arquivos fornecidos.
- Zip Odete inclui notebooks + cópia das bases (requisito do enunciado).
- Specs e ADRs referenciam `notebooks/` e `data/base_XX/`, não `src/`.
