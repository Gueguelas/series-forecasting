# SPEC — Relatório e entrega

**Versão:** 0.2  
**PRD:** seções 10, 11, 12, 13  
**ADR:** 0004

## 1. Formatos e localização

| Formato | Origem | Observação |
|---------|--------|------------|
| Análise por base | `notebooks/base_01.ipynb` … `base_05.ipynb` | Entrega principal por dataset |
| Relatório consolidado | `notebooks/relatorio.ipynb` | Narrativa final + export HTML/PDF |
| HTML paginado | Export de `relatorio.ipynb` | Material da apresentação oral |
| PDF | Export de `relatorio.ipynb` | Mesmo conteúdo do HTML |

## 2. Conteúdo de cada `base_XX.ipynb`

Pipeline completo da base (autocontido):

1. Documentação e EDA
2. Limpeza e feature engineering
3. STL e força da sazonalidade
4. Walk-forward dos 4 modelos
5. Hiperparâmetros e otimização
6. MAE e ranking na base
7. Resíduos, ACF, Ljung-Box
8. Feature importance (RF + especialização)

## 3. Conteúdo de `relatorio.ipynb`

Consolida os 5 notebooks e gera a narrativa comparativa:

1. Resumo executivo
2. Integrantes e responsabilidades
3. Documentação das 5 bases (síntese)
4. Limpeza, preparação e feature engineering (síntese)
5. STL, tendência e força da sazonalidade
6. Protocolo walk-forward
7. Modelos, hiperparâmetros e otimização
8. Resultados comparativos por MAE (tabela consolidada)
9. Resíduos e Ljung-Box (tabela consolidada no corpo)
10. Importância das features
11. Estudo aprofundado do modelo de especialização
12. Conclusões, limitações e recomendações
13. Referências
14. Apêndices + registro de demandas (entrega professor)

Pode importar resultados dos notebooks de base via `%run` ou leitura de outputs salvos.

## 4. Apresentação oral

- Usar relatório HTML como material visual (sem slides separados)
- Todos os integrantes participam
- Priorizar interpretação, não leitura integral

## 5. Registro de demandas

Tabela diária conforme [`RULES.md`](../RULES.md) seção 9 — no apêndice do `relatorio.ipynb`.

## 6. Pacote Odete

`Grupo_03_Trabalho_Series_Temporais.zip` contendo:

- [ ] PDF final
- [ ] HTML paginado
- [ ] `notebooks/*.ipynb` (fonte)
- [ ] `data/base_XX/` (bases utilizadas)
- [ ] Consolidado MAE
- [ ] Registro de demandas

## 7. Qualidade

- Narrativa comparativa (não dump de código)
- Citações de fontes, bibliotecas e referências
- Gráficos relevantes no corpo; complementares no apêndice
- Reprodutível: notebooks + `data/` + `requirements.txt`
