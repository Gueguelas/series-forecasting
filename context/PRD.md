# PRD — Modelagem Comparativa de Séries Temporais

**Status:** Rascunho  
**Grupo:** 3  
**Modelo de especialização:** Elastic Net (regressão linear regularizada)  
**Slug do modelo:** `elastic_net`  
**Fonte:** `docs/instrucoes.pdf`

---

## 1. Problema

Comparar criticamente quatro abordagens de previsão (três comuns + uma de especialização) em **cinco bases temporais compartilhadas**, incorporando variáveis externas quando compatíveis, com validação realista e métrica unificada.

## 2. Objetivos

| # | Objetivo | Critério de sucesso |
|---|----------|---------------------|
| O1 | Documentar e explorar 5 bases com variáveis externas | Dicionário, EDA, gráficos e decisões de limpeza documentados |
| O2 | Decompor séries via STL | Tendência, sazonalidade, residual e força da sazonalidade interpretados |
| O3 | Feature engineering sem vazamento | Features coerentes com horizonte; mesmas features em RF e especialização |
| O4 | Ajustar e comparar 4 modelos por base | 20 combinações (5 bases × 4 modelos) executadas |
| O5 | Otimizar hiperparâmetros | Busca documentada; teste final com hiperparâmetros fixos |
| O6 | Avaliar por MAE (walk-forward) | MAE fora da amostra; ranking por base |
| O7 | Analisar resíduos | Gráficos, ACF, Ljung-Box com tabela consolidada no relatório |
| O8 | Interpretar importância de features | RF + especialização; método compatível por modelo |
| O9 | Comunicar resultados | Relatório HTML/PDF, apresentação oral, registro de demandas |

## 3. Escopo

### In scope

- 5 bases congeladas (versão única para toda a turma)
- Modelos comuns: **SARIMAX**, **Holt-Winters** (univariado), **Random Forest**
- Modelo de especialização do grupo (ver tabela abaixo)
- Validação walk-forward com mesmas origens, horizonte e conjunto de teste
- Relatório técnico HTML paginado + PDF
- Registro diário de demandas por integrante
- Entrega compactada na Plataforma Odete

### Out of scope

- Slides separados para apresentação (usa o relatório HTML)
- Média ou soma de MAE entre bases (escalas diferentes)
- Uso de valores futuros não disponíveis na data de origem da previsão

## 4. Modelos por grupo

| Grupo | Modelo de especialização | Família |
|-------|--------------------------|---------|
| 1 | XGBoost Regressor | Boosting |
| 2 | Support Vector Regression (SVR) | Margem |
| 3 | Elastic Net | Regressão regularizada |
| 4 | MLP Regressor | Rede neural |
| 5 | PLS Regression | Componentes supervisionados |

**Modelos comuns (todos os grupos):** SARIMAX, Holt-Winters, Random Forest.

## 5. Requisitos das bases

Cada base deve:

- Ter variável-alvo numérica com frequência regular (ou regularizada)
- Conter observações e ciclos sazonais suficientes
- Possuir ≥ 2 variáveis externas potencialmente relacionadas ao alvo
- Documentar fonte, período, unidade, frequência e significado
- Permitir definir horizonte de previsão e data de origem

## 6. Entregáveis

> **Formato de trabalho:** toda a análise é feita em **notebooks** (`notebooks/`). Os dados são **fornecidos ao grupo** e ficam em `data/` (gitignored), um diretório por dataset.

| Entregável | Formato | Local no repo |
|------------|---------|---------------|
| Análise por dataset (×5) | `.ipynb` | `notebooks/base_01.ipynb` … `base_05.ipynb` |
| Relatório final | PDF | Exportado de `notebooks/relatorio.ipynb` |
| Relatório paginado | HTML autocontido | Exportado de `notebooks/relatorio.ipynb` |
| Código-fonte do relatório | `.ipynb` | `notebooks/relatorio.ipynb` |
| Bases utilizadas | Arquivos originais | `data/base_XX/` (local; incluir no zip Odete) |
| Resultados MAE | Tabela consolidada | Gerada nos notebooks / seção do `relatorio.ipynb` |
| Registro de demandas | Tabela no relatório (apêndice professor) | `relatorio.ipynb` |

Cada notebook de base deve ser **autocontido e reprodutível**: EDA, STL, features, 4 modelos, walk-forward, MAE, resíduos e feature importance daquela base.

**Nome sugerido do zip:** `Grupo_03_Trabalho_Series_Temporais.zip`

## 7. Estrutura mínima do relatório

1. Resumo executivo
2. Integrantes e divisão de responsabilidades
3. Documentação das 5 bases
4. Limpeza, preparação e feature engineering
5. STL, tendência e força da sazonalidade
6. Protocolo walk-forward
7. Modelos, hiperparâmetros e otimização
8. Resultados comparativos por MAE
9. Análise de resíduos e Ljung-Box
10. Importância das features
11. Estudo do modelo de especialização
12. Conclusões, limitações e recomendações
13. Referências
14. Apêndices e registro de demandas (entrega ao professor)

## 8. Critérios de avaliação (pesos)

| Critério | Peso |
|----------|------|
| Documentação das 5 bases | 5% |
| STL e sazonalidade | 5% |
| Feature engineering e anti-vazamento | 10% |
| Modelos e walk-forward | 15% |
| Hiperparâmetros | 10% |
| Comparação por MAE | 10% |
| Resíduos, ACF, Ljung-Box | 5% |
| Modelo escolhido e feature importance | 20% |
| Qualidade HTML/PDF | 10% |
| Apresentação oral | 5% |
| Gestão de demandas | 5% |

## 9. Restrições e premissas

- **Entregas em notebooks** — não há pacote `src/`; código reprodutível vive em `notebooks/`
- **Dados fornecidos ao grupo** — cada integrante mantém `data/base_XX/` localmente (pasta no `.gitignore`)
- Resultados reproduzíveis a partir dos notebooks + bases no zip
- Bases congeladas — alteração exige aprovação prévia
- Uso de IA exige revisão crítica e responsabilidade do grupo
- Holt-Winters é referência univariada (sem variáveis externas)

## 10. Integrantes

| Nome | Papel principal | Contato |
|------|-----------------|---------|
| [DEFINIR] | | |
| [DEFINIR] | | |
| [DEFINIR] | | |
