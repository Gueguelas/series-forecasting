# AGENTS — Instruções para agentes de IA

Este documento orienta agentes (Cursor, Copilot, etc.) que trabalham neste repositório acadêmico.

## Missão

Auxiliar o grupo na implementação reprodutível do trabalho de séries temporais, **sem substituir** o entendimento crítico dos integrantes. Todo código e texto gerado deve ser revisado por humanos.

## Leitura obrigatória antes de agir

1. [`context/README.md`](README.md) — precedência de documentos
2. [`PRD.md`](PRD.md) — escopo e entregáveis
3. [`RULES.md`](RULES.md) — especialmente regras de git
4. ADRs vigentes em [`adr/`](adr/)
5. Spec aplicável em [`specs/`](specs/)
6. [`docs/instrucoes.pdf`](../docs/instrucoes.pdf) — quando houver dúvida sobre requisitos

## Comportamento esperado

### Fazer

- Seguir o protocolo walk-forward e a métrica MAE (ADR-0001, ADR-0002)
- Garantir que features não usem informação futura (ADR-0003)
- Reutilizar o mesmo conjunto de features em Random Forest e modelo de especialização
- Documentar decisões metodológicas; propor ADR quando a decisão for estrutural
- Implementar análise em **notebooks** em `notebooks/` — um por dataset (ADR-0004)
- Carregar/salvar dados em `../data/base_XX/` com nomenclatura ADR-0005 (`cleaned_{base_id}.csv`, etc.)
- Salvar modelos treinados em `../artifacts/base_XX/{modelo}.pkl`
- Usar seeds fixos e versões de bibliotecas pinadas para reprodutibilidade
- Atualizar [`HANDOFF.md`](HANDOFF.md) ao encerrar sessões com trabalho relevante
- Escrever em português nos documentos de contexto e relatório; código e nomes de variáveis em inglês

### Não fazer

- **Commit ou push** sem solicitação explícita de um integrante (ver [`RULES.md`](RULES.md))
- Alterar bases congeladas sem ADR e aprovação do grupo
- Usar o conjunto de teste final para escolher hiperparâmetros
- Somar ou calcular média de MAE entre bases de escalas diferentes
- Introduzir dependências pesadas sem justificativa
- Copiar código sem compreensão — o enunciado exige responsabilidade sobre resultados

## Fluxo de trabalho sugerido

```
1. Ler contexto (PRD → SDD → ADR → Spec)
2. Confirmar escopo da tarefa com HANDOFF anterior
3. Implementar mudança mínima necessária
4. Validar anti-leakage e reprodutibilidade
5. Registrar HANDOFF
6. Aguardar humano revisar e autorizar commit (se aplicável)
```

## Domínios e specs

| Tarefa | Spec |
|--------|------|
| Carregar/limpar bases | `specs/spec-dados.md` |
| Lags, janelas, calendário | `specs/spec-feature-engineering.md` |
| Walk-forward | `specs/spec-validacao.md` |
| SARIMAX, HW, RF, especialização | `specs/spec-modelos.md` |
| MAE, resíduos, Ljung-Box | `specs/spec-avaliacao.md` |
| HTML/PDF | `specs/spec-relatorio.md` |

## Modelos do projeto

| Modelo | Variáveis externas | Feature importance |
|--------|-------------------|-------------------|
| SARIMAX | Sim | Coeficientes |
| Holt-Winters | Não (univariado) | Nível, tendência, sazonalidade |
| Random Forest | Sim | Nativa / Permutation |
| Especialização [DEFINIR] | Sim (se compatível) | Conforme modelo (ver enunciado) |

## Quando criar uma ADR

- Escolha de horizonte, origens walk-forward ou período sazonal global
- Mudança de base, modelo ou protocolo de validação
- Decisão de stack (bibliotecas, formato de relatório)
- Tratamento de variável externa com disponibilidade ambígua

Use o template em [`adr/0000-template.md`](adr/0000-template.md).

## Formato de resposta

- Explicar **por que** uma decisão metodológica foi tomada
- Citar trechos do enunciado ou ADR quando relevante
- Indicar arquivos alterados e validações pendentes
- Não assumir número do grupo nem modelo de especialização — perguntar se não estiver definido

## Handoff

Ao final de sessões com alterações, preencher seção em [`HANDOFF.md`](HANDOFF.md) seguindo o template. Não fazer commit do handoff sem autorização.
